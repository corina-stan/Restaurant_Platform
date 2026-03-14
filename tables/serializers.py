from rest_framework import serializers
from .models import Table, QRSession


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ('id', 'number', 'name', 'is_active')


class QRSessionSerializer(serializers.ModelSerializer):
    table = TableSerializer(read_only=True)

    class Meta:
        model = QRSession
        fields = ('id', 'table', 'token', 'created_at', 'is_active')