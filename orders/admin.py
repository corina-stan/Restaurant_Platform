from django.contrib import admin
from .models import Order, OrderGroup, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'session', 'waiter', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'unit_price', 'status', 'created_at')
    list_filter = ('status',)