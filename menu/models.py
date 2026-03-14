from django.db import models

class Category(models.Model):
    class Department(models.TextChoices):
        KITCHEN = 'kitchen', 'Bucătărie'
        BAR = 'bar', 'Bar'

    name = models.CharField(max_length=100)
    department = models.CharField(
        max_length=10,
        choices=Department.choices
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.department})"


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    prep_time = models.PositiveIntegerField(
        default=0,
        help_text="Timp de preparare în minute"
    )
    is_available = models.BooleanField(default=True)
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.price} lei"