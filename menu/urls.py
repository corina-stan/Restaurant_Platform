from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet, basename='product')
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeItemViewSet, basename='recipe')
router.register('receipts', views.StockReceiptViewSet)
router.register('purchase_invoices', views.PurchaseInvoiceViewSet, basename='purchase_invoice')

urlpatterns = [
    path('', include(router.urls)),
]