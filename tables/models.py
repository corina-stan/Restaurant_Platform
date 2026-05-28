from django.db import models
import uuid

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Masa {self.number}"


class QRSession(models.Model):
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Client interaction states
    waiter_called = models.BooleanField(default=False)
    bill_requested = models.BooleanField(default=False)
    bill_payment_method = models.CharField(max_length=10, blank=True, null=True)  # 'cash' | 'card' | 'ticket'
    bill_tip = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Sesiune masa {self.table.number} - {self.token}"