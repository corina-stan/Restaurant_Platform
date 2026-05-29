from decimal import Decimal, InvalidOperation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsWaiter, IsBarman, IsStaff, IsAdmin
from orders.models import Order, OrderGroup, OrderItem
from .models import Payment, ZReport
from .serializers import PaymentSerializer, ZReportSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction
from django.db.models import Max
from tables.views import run_auto_migrations
from django.utils import timezone



class CreatePaymentView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        order_id = request.data.get('order_id')
        group_id = request.data.get('group_id')
        method = request.data.get('method')
        
        try:
            tip_val = request.data.get('tip', 0)
            if tip_val is None:
                tip_val = 0
            tip = Decimal(str(tip_val))
        except (InvalidOperation, ValueError, TypeError):
            tip = Decimal('0.00')

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

        if order.status == 'closed':
            from django.utils import timezone
            session = order.session
            if session:
                session.is_active = False
                session.closed_at = timezone.now()
                session.save()

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
                'group_id': group.id if group else None,
            }
        )

        async_to_sync(channel_layer.group_send)(
            f'table_{order.session.table.number}',
            {
                'type': 'payment_completed',
                'order_id': order.id,
                'group_id': group.id if group else None,
            }
        )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )


def calculate_aggregates(payments_queryset):
    # Retrieve payments with prefetch of items and products for exact calculations
    payments = list(payments_queryset.select_related('order', 'group'))

    total_amount = Decimal('0.00')
    total_tip = Decimal('0.00')
    
    cash_amount = Decimal('0.00')
    card_amount = Decimal('0.00')
    ticket_amount = Decimal('0.00')
    
    cash_tip = Decimal('0.00')
    card_tip = Decimal('0.00')
    ticket_tip = Decimal('0.00')
    
    vat_11_gross = Decimal('0.00')
    vat_11_net = Decimal('0.00')
    vat_11_amount = Decimal('0.00')
    
    vat_21_gross = Decimal('0.00')
    vat_21_net = Decimal('0.00')
    vat_21_amount = Decimal('0.00')
    
    for p in payments:
        amount = Decimal(str(p.amount))
        tip = Decimal(str(p.tip))
        total_amount += amount
        total_tip += tip
        
        if p.method == 'cash':
            cash_amount += amount
            cash_tip += tip
        elif p.method == 'card':
            card_amount += amount
            card_tip += tip
        elif p.method == 'ticket':
            ticket_amount += amount
            ticket_tip += tip
            
        # VAT calculations based on active items in order or group
        if p.group:
            items = list(OrderItem.objects.filter(group=p.group).exclude(status='rejected').select_related('product__category'))
        else:
            items = list(OrderItem.objects.filter(order=p.order).exclude(status='rejected').select_related('product__category'))
            
        for item in items:
            qty = Decimal(str(item.quantity))
            price = Decimal(str(item.unit_price))
            item_gross = qty * price
            
            # Determine VAT rate based on category department
            rate = 11
            if item.product and item.product.category:
                if item.product.category.department == 'bar':
                    rate = 21
                    
            if rate == 21:
                item_net = item_gross / Decimal('1.21')
                item_vat = item_gross - item_net
                vat_21_gross += item_gross
                vat_21_net += item_net
                vat_21_amount += item_vat
            else:
                item_net = item_gross / Decimal('1.11')
                item_vat = item_gross - item_net
                vat_11_gross += item_gross
                vat_11_net += item_net
                vat_11_amount += item_vat
                
    return {
        'total_amount': total_amount,
        'total_tip': total_tip,
        'cash_amount': cash_amount,
        'card_amount': card_amount,
        'ticket_amount': ticket_amount,
        'cash_tip': cash_tip,
        'card_tip': card_tip,
        'ticket_tip': ticket_tip,
        'vat_11_gross': vat_11_gross,
        'vat_11_net': vat_11_net,
        'vat_11_amount': vat_11_amount,
        'vat_21_gross': vat_21_gross,
        'vat_21_net': vat_21_net,
        'vat_21_amount': vat_21_amount,
        'payments_count': len(payments)
    }


class ShiftReportView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        run_auto_migrations()
        payments_qs = Payment.objects.filter(
            collected_by=request.user,
            z_report__isnull=True,
            status='completed'
        )

        detailed = request.query_params.get('detailed', 'false').lower() == 'true'
        aggregates = calculate_aggregates(payments_qs)
        
        response_data = {
            'waiter_username': request.user.username,
            'created_at': timezone.now().isoformat(),
            'total_amount': aggregates['total_amount'],
            'total_tip': aggregates['total_tip'],
            'cash_amount': aggregates['cash_amount'],
            'card_amount': aggregates['card_amount'],
            'ticket_amount': aggregates['ticket_amount'],
            'cash_tip': aggregates['cash_tip'],
            'card_tip': aggregates['card_tip'],
            'ticket_tip': aggregates['ticket_tip'],
            'vat_11_gross': aggregates['vat_11_gross'],
            'vat_11_net': aggregates['vat_11_net'],
            'vat_11_amount': aggregates['vat_11_amount'],
            'vat_21_gross': aggregates['vat_21_gross'],
            'vat_21_net': aggregates['vat_21_net'],
            'vat_21_amount': aggregates['vat_21_amount'],
            'payments_count': aggregates['payments_count'],
        }

        if detailed:
            ordered_payments = payments_qs.order_by('created_at')
            response_data['payments'] = PaymentSerializer(ordered_payments, many=True).data

        return Response(response_data)


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


class RecentPaymentsView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        if request.user.role == 'admin':
            payments = Payment.objects.filter(status='completed')
        else:
            payments = Payment.objects.filter(status='completed', collected_by=request.user)
        
        payments = payments.select_related('order', 'collected_by').prefetch_related('order__items__product').order_by('-created_at')[:50]
        return Response(PaymentSerializer(payments, many=True).data)


class CreateZReportView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        run_auto_migrations()
        try:
            with transaction.atomic():
                payment_ids = list(Payment.objects.filter(
                    collected_by=request.user,
                    z_report__isnull=True,
                    status='completed'
                ).values_list('id', flat=True))

                if not payment_ids:
                    return Response(
                        {'error': 'Nu există tranzacții finalizate neînchise în această tură.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                payments_qs = Payment.objects.filter(id__in=payment_ids).order_by().select_for_update(of=('self',))

                aggregates = calculate_aggregates(payments_qs)

                next_number = (ZReport.objects.aggregate(Max('number'))['number__max'] or 0) + 1

                z_report = ZReport.objects.create(
                    number=next_number,
                    waiter=request.user,
                    total_amount=aggregates['total_amount'],
                    total_tip=aggregates['total_tip'],
                    cash_amount=aggregates['cash_amount'],
                    card_amount=aggregates['card_amount'],
                    ticket_amount=aggregates['ticket_amount'],
                    cash_tip=aggregates['cash_tip'],
                    card_tip=aggregates['card_tip'],
                    ticket_tip=aggregates['ticket_tip'],
                    vat_11_gross=aggregates['vat_11_gross'],
                    vat_11_net=aggregates['vat_11_net'],
                    vat_11_amount=aggregates['vat_11_amount'],
                    vat_21_gross=aggregates['vat_21_gross'],
                    vat_21_net=aggregates['vat_21_net'],
                    vat_21_amount=aggregates['vat_21_amount'],
                    payments_count=aggregates['payments_count']
                )

                # Link the payments to the ZReport
                payments_qs.update(z_report=z_report)

                return Response(
                    ZReportSerializer(z_report).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {'error': f'Eroare la generarea raportului Z: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )