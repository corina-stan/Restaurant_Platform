from django.db import models
from orders.models import Order, OrderGroup
from accounts.models import User


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Numerar'
        CARD = 'card', 'Card'
        TICKET = 'ticket', 'Tichet de masă'

    class Status(models.TextChoices):
        PENDING = 'pending', 'În așteptare'
        COMPLETED = 'completed', 'Finalizată'
        CANCELLED = 'cancelled', 'Anulată'

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    group = models.ForeignKey(
        OrderGroup,
        on_delete=models.PROTECT,
        related_name='payments',
        null=True,
        blank=True
    )
    collected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='payments_collected',
        null=True,
        blank=True
    )
    method = models.CharField(
        max_length=10,
        choices=Method.choices
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tip = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plată {self.method} - {self.amount} lei - Comanda #{self.order.pk}"

    def get_total(self):
        return self.amount + self.tip