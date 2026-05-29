from rest_framework import serializers
from .models import Payment, ZReport
from orders.serializers import OrderSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order_details = OrderSerializer(source='order', read_only=True)
    total = serializers.SerializerMethodField()
    collected_by_username = serializers.CharField(
        source='collected_by.username',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'order_details', 'group',
            'method', 'amount', 'tip', 'status',
            'collected_by', 'collected_by_username',
            'created_at', 'total'
        )
        read_only_fields = ('collected_by', 'created_at', 'status')

    def get_total(self, obj):
        return obj.get_total()


class ZReportSerializer(serializers.ModelSerializer):
    waiter_username = serializers.CharField(source='waiter.username', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = ZReport
        fields = (
            'id', 'number', 'waiter', 'waiter_username', 'created_at',
            'total_amount', 'total_tip', 'cash_amount', 'card_amount',
            'ticket_amount', 'cash_tip', 'card_tip', 'ticket_tip',
            'vat_11_gross', 'vat_11_net', 'vat_11_amount',
            'vat_21_gross', 'vat_21_net', 'vat_21_amount',
            'payments_count', 'payments'
        )