from rest_framework import serializers
from .models import Order, OrderGroup, OrderItem
from menu.serializers import ProductSerializer


class PaymentSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    group = serializers.SerializerMethodField()
    method = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tip = serializers.DecimalField(max_digits=8, decimal_places=2)
    status = serializers.CharField()

    def get_group(self, obj):
        return obj.group.id if obj.group else None

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('menu.models', fromlist=['Product']).Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_id', 'quantity',
            'unit_price', 'status', 'rejection_reason',
            'created_at', 'group', 'notes'
        )
        read_only_fields = ('unit_price', 'status', 'created_at')


class OrderGroupSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderGroup
        fields = ('id', 'name', 'items', 'total')

    def get_total(self, obj):
        return sum(
            item.get_total()
            for item in obj.items.all()
            if item.status != 'rejected'
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    groups = OrderGroupSerializer(many=True, read_only=True)
    payments = PaymentSummarySerializer(many=True, read_only=True)
    table_number = serializers.IntegerField(
        source='session.table.number',
        read_only=True
    )
    bill_requested = serializers.BooleanField(source='session.bill_requested', read_only=True)
    bill_payment_method = serializers.CharField(source='session.bill_payment_method', read_only=True)
    bill_tip = serializers.DecimalField(source='session.bill_tip', max_digits=8, decimal_places=2, read_only=True)
    waiter_called = serializers.BooleanField(source='session.waiter_called', read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'session', 'waiter', 'status',
            'created_at', 'updated_at', 'notes',
            'items', 'groups', 'table_number', 'total', 'payments',
            'bill_requested', 'bill_payment_method', 'bill_tip', 'waiter_called'
        )
        read_only_fields = ('created_at', 'updated_at', 'waiter')

    def get_total(self, obj):
        return sum(
            item.get_total()
            for item in obj.items.all()
            if item.status != 'rejected'
        )


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    group_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class CreateOrderSerializer(serializers.Serializer):
    session_token = serializers.UUIDField()
    order_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = CreateOrderItemSerializer(many=True)