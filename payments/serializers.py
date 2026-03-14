from rest_framework import serializers
from .models import Payment
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