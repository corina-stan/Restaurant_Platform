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
    requires_recipe = models.BooleanField(
        default=True,
        help_text="Debifează dacă produsul se vinde direct și nu necesită deducere din stoc"
    )
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.price} lei"


class Ingredient(models.Model):
    name = models.CharField(max_length=150, unique=True)
    unit = models.CharField(
        max_length=20,
        help_text="ex: kg, litru, buc, g, ml"
    )
    current_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        default=0.000
    )

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"


class RecipeItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='recipe_items'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='used_in'
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        help_text="Cantitatea din acest ingredient necesară pentru 1 porție"
    )

    class Meta:
        unique_together = ('product', 'ingredient')

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} de {self.ingredient.name} pentru {self.product.name}"


class PurchaseInvoice(models.Model):
    invoice_number = models.CharField(max_length=50)
    supplier_name = models.CharField(max_length=150)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.supplier_name}"

class StockReceipt(models.Model):
    invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=True
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='receipts'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price_without_vat = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Preț achiziție per unitate fără TVA"
    )
    vat_rate = models.PositiveIntegerField(
        default=9,
        help_text="Cota TVA (ex: 9, 11, 19, 21)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"+{self.quantity} {self.ingredient.unit} {self.ingredient.name} la {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # Creștem stocul ingredientului la momentul creării recepției
            self.ingredient.current_stock += self.quantity
            self.ingredient.save()