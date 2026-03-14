from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        WAITER = 'waiter', 'Ospătar'
        BARMAN = 'barman', 'Barman'
        KITCHEN = 'kitchen', 'Bucătărie'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"