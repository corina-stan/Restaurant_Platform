from django.db import models
from tables.models import QRSession
from menu.models import Product
from accounts.models import User


class Order(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Deschisă'
        CLOSED = 'closed', 'Închisă'
        CANCELLED = 'cancelled', 'Anulată'

    session = models.ForeignKey(
        QRSession,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    waiter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Comanda #{self.pk} - Masa {self.session.table.number}"


class OrderGroup(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='groups'
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"Grup '{self.name}' - Comanda #{self.order.pk}"


class OrderItem(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'În așteptare'
        IN_PROGRESS = 'in_progress', 'În lucru'
        READY = 'ready', 'Gata'
        SERVED = 'served', 'Servit'
        REJECTED = 'rejected', 'Refuzat'

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    group = models.ForeignKey(
        OrderGroup,
        on_delete=models.SET_NULL,
        related_name='items',
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING
    )
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True) 
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - {self.status}"

    def get_total(self):
        return self.quantity * self.unit_price