from rest_framework import serializers
from .models import Category, Product, Ingredient, RecipeItem, StockReceipt, PurchaseInvoice, Supplier


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'department')


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    has_recipe = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'price',
            'prep_time', 'is_available', 'requires_recipe', 'image', 'category', 'category_id', 'has_recipe'
        )

    def get_has_recipe(self, obj):
        return obj.recipe_items.exists()

class IngredientSerializer(serializers.ModelSerializer):
    last_purchased_quantity = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = '__all__'

    def get_last_purchased_quantity(self, obj):
        qty = obj.get_last_purchased_quantity()
        if qty is not None:
            return float(qty)
        return None

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()

class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)

    class Meta:
        model = RecipeItem
        fields = ('id', 'product', 'ingredient', 'ingredient_name', 'ingredient_unit', 'quantity')

class StockReceiptSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    
    class Meta:
        model = StockReceipt
        fields = ('id', 'invoice', 'ingredient', 'ingredient_name', 'ingredient_unit', 'quantity', 'unit_price_without_vat', 'vat_rate', 'created_at')
        read_only_fields = ('created_at',)

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    items = StockReceiptSerializer(many=True, read_only=True)
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source='supplier',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PurchaseInvoice
        fields = ('id', 'nir_number', 'invoice_number', 'supplier_name', 'supplier', 'supplier_id', 'date', 'created_at', 'items')
        read_only_fields = ('created_at',)