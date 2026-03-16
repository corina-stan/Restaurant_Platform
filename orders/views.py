from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from accounts.permissions import IsWaiter, IsBarman, IsKitchen, IsStaff
from tables.models import QRSession
from menu.models import Product
from .models import Order, OrderGroup, OrderItem
from .serializers import (
    OrderSerializer, CreateOrderSerializer, OrderItemSerializer
)


class CreateOrderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = QRSession.objects.get(
                token=serializer.validated_data['session_token'],
                is_active=True
            )
        except QRSession.DoesNotExist:
            return Response(
                {'error': 'Sesiune invalidă sau expirată.'},
                status=status.HTTP_404_NOT_FOUND
            )

        order = Order.objects.create(
            session=session,
            notes=serializer.validated_data.get('notes', '')
        )

        for item_data in serializer.validated_data['items']:
            try:
                product = Product.objects.get(
                    id=item_data['product_id'],
                    is_available=True
                )
            except Product.DoesNotExist:
                order.delete()
                return Response(
                    {'error': f'Produsul {item_data["product_id"]} nu există sau nu e disponibil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            group = None
            if item_data.get('group_id'):
                try:
                    group = OrderGroup.objects.get(
                        id=item_data['group_id'],
                        order=order
                    )
                except OrderGroup.DoesNotExist:
                    pass

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                unit_price=product.price,
                group=group
            )

            # Notificare real-time
            channel_layer = get_channel_layer()
            department = product.category.department
            async_to_sync(channel_layer.group_send)(
            department,
            {
                'type': 'new_order_item',
                'order_id': order.id,
                'item_id': OrderItem.objects.filter(order=order, product=product).last().id,
                'product_id': product.id,  
                'product_name': product.name,
                'quantity': item_data['quantity'],
                'table_number': session.table.number,
                'notes': order.notes,
                'timestamp': timezone.now().isoformat()
            }
)

        # Notificare ospatar - comanda noua
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'waiters',
            {
                'type': 'new_order',
                'order_id': order.id,
                'table_number': session.table.number,
            }
        )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_id):
        try:
            order = Order.objects.prefetch_related(
                'items__product__category',
                'groups__items__product'
            ).get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Comanda nu există.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(OrderSerializer(order).data)


class TableOrdersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, table_number):
        orders = Order.objects.filter(
            session__table__number=table_number,
            status='open'
        ).prefetch_related('items__product__category', 'groups')
        return Response(OrderSerializer(orders, many=True).data)


class AllOpenOrdersView(APIView):
    permission_classes = [IsStaff]

    def get(self, request):
        orders = Order.objects.filter(
            status='open'
        ).prefetch_related(
            'items__product__category',
            'groups'
        ).order_by('created_at')
        return Response(OrderSerializer(orders, many=True).data)


class UpdateOrderItemStatusView(APIView):
    permission_classes = [IsStaff]

    def patch(self, request, item_id):
        try:
            item = OrderItem.objects.select_related(
                'product__category'
            ).get(id=item_id)
        except OrderItem.DoesNotExist:
            return Response(
                {'error': 'Item-ul nu există.'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')
        rejection_reason = request.data.get('rejection_reason', '')

        valid_statuses = ['pending', 'in_progress', 'ready', 'served', 'rejected']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Status invalid. Valori permise: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        department = item.product.category.department
        user_role = request.user.role

        if department == 'kitchen' and user_role not in ['kitchen', 'admin', 'waiter']:
            return Response(
                {'error': 'Nu ai permisiunea să modifici acest item.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if department == 'bar' and user_role not in ['barman', 'admin', 'waiter']:
            return Response(
                {'error': 'Nu ai permisiunea să modifici acest item.'},
                status=status.HTTP_403_FORBIDDEN
            )

        item.status = new_status
        if new_status == 'rejected':
            item.rejection_reason = rejection_reason
        item.save()

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f'table_{item.order.session.table.number}',
            {
                'type': 'order_update',
                'order_id': item.order.id,
                'item_id': item.id,
                'status': new_status,
                'product_name': item.product.name,
                'message': f'{item.product.name} - {new_status}'
            }
        )

        if new_status == 'ready':
            async_to_sync(channel_layer.group_send)(
                'waiters',
                {
                    'type': 'item_ready',
                    'item_id': item.id,
                    'product_name': item.product.name,
                    'table_number': item.order.session.table.number,
                    'order_id': item.order.id
                }
            )

        return Response(OrderItemSerializer(item).data)