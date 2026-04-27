from rest_framework import serializers
from .models import Category, Product, Ingredient, RecipeItem, StockReceipt, PurchaseInvoice


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
            'prep_time', 'is_available', 'requires_recipe', 'category', 'category_id', 'has_recipe'
        )

    def get_has_recipe(self, obj):
        return obj.recipe_items.exists()

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

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

class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    items = StockReceiptSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = ('id', 'invoice_number', 'supplier_name', 'date', 'created_at', 'items')
        read_only_fields = ('created_at',)