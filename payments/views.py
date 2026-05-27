from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsWaiter, IsBarman, IsStaff, IsAdmin
from orders.models import Order, OrderGroup, OrderItem
from .models import Payment
from .serializers import PaymentSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class CreatePaymentView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        order_id = request.data.get('order_id')
        group_id = request.data.get('group_id')
        method = request.data.get('method')
        tip = request.data.get('tip', 0)

        if not order_id or not method:
            return Response(
                {'error': 'order_id și method sunt obligatorii.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_methods = ['cash', 'card', 'ticket']
        if method not in valid_methods:
            return Response(
                {'error': f'Metodă invalidă. Valori permise: {valid_methods}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Comanda nu există.'},
                status=status.HTTP_404_NOT_FOUND
            )

        group = None
        if group_id:
            try:
                group = OrderGroup.objects.get(id=group_id, order=order)
            except OrderGroup.DoesNotExist:
                return Response(
                    {'error': 'Grupul nu există în această comandă.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        if group:
            items = OrderItem.objects.filter(
                order=order,
                group=group
            ).exclude(status='rejected')
        else:
            items = OrderItem.objects.filter(
                order=order
            ).exclude(status='rejected')

        amount = sum(item.get_total() for item in items)

        payment = Payment.objects.create(
            order=order,
            group=group,
            method=method,
            amount=amount,
            tip=tip,
            collected_by=request.user,
            status='completed'
        )

        if group:
            paid_group_ids = set(
                Payment.objects.filter(
                    order=order,
                    status='completed'
                ).values_list('group_id', flat=True)
            )
            all_group_ids = set(
                order.groups.values_list('id', flat=True)
            )
            if all_group_ids and all_group_ids == paid_group_ids:
                order.status = 'closed'
                order.save()
        else:
            order.status = 'closed'
            order.save()

        from orders.models import log_operation
        method_label = payment.get_method_display()
        if group:
            desc = f"A fost înregistrată plata de {amount:.2f} lei (+ bacșiș {tip:.2f} lei) prin {method_label} pentru grupul '{group.name}' din comanda #{order.id}. Starea comenzii: {order.get_status_display()}."
        else:
            desc = f"A fost înregistrată plata de {amount:.2f} lei (+ bacșiș {tip:.2f} lei) prin {method_label} pentru comanda #{order.id}. Starea comenzii: {order.get_status_display()}."
        
        log_operation(
            user=request.user,
            order=order,
            operation_type="Plată și Închidere",
            description=desc
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'waiters',
            {
                'type': 'payment_completed',
                'order_id': order.id,
                'table_number': order.session.table.number,
            }
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )


class ShiftReportView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        payments = Payment.objects.filter(
            status='completed',
            collected_by=request.user
        )

        cash_total = sum(
            p.get_total() for p in payments if p.method == 'cash'
        )
        card_total = sum(
            p.get_total() for p in payments if p.method == 'card'
        )
        ticket_total = sum(
            p.get_total() for p in payments if p.method == 'ticket'
        )
        tips_total = sum(p.tip for p in payments)

        return Response({
            'total_incasat': cash_total + card_total + ticket_total,
            'cash': cash_total,
            'card': card_total,
            'tichete': ticket_total,
            'bacsis_total': tips_total,
            'numar_tranzactii': payments.count(),
        })


class OrderPaymentsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Comanda nu există.'},
                status=status.HTTP_404_NOT_FOUND
            )

        payments = Payment.objects.filter(order=order)
        return Response(PaymentSerializer(payments, many=True).data)