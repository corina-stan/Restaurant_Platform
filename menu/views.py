from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsAdmin, IsBarman, IsKitchen, IsStaff
from .models import Category, Product, Ingredient, RecipeItem, StockReceipt, PurchaseInvoice, Supplier
from .serializers import CategorySerializer, ProductSerializer, IngredientSerializer, RecipeItemSerializer, StockReceiptSerializer, PurchaseInvoiceSerializer, SupplierSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from orders.models import OrderItem
from decimal import Decimal


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdmin()]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_queryset(self):
        queryset = Product.objects.select_related('category').all()
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(category__department=department)
        available_only = self.request.query_params.get('available_only')
        if available_only == 'true':
            queryset = queryset.filter(is_available=True)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'toggle_availability':
            return [IsStaff()]    # schimbă din IsBarman/IsKitchen în IsStaff
        return [IsAdmin()]

    def _is_bar_product(self):
        try:
            product = self.get_object()
            return product.category.department == 'bar'
        except:
            return False

    @action(detail=True, methods=['patch'])
    def toggle_availability(self, request, pk=None):
        product = self.get_object()
        product.is_available = not product.is_available
        product.save()

        if not product.is_available:
            OrderItem.objects.filter(
                product=product,
                status__in=['pending', 'in_progress'],
                order__status='open'
            ).update(
                status='rejected',
                rejection_reason='Produs indisponibil'
            )

        channel_layer = get_channel_layer()
        
        for group in ['kitchen', 'bar', 'waiters']:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    'type': 'product_availability',
                    'product_id': product.id,
                    'is_available': product.is_available,
                    'product_name': product.name,
                }
            )

        from tables.models import Table
        for table in Table.objects.filter(is_active=True):
            async_to_sync(channel_layer.group_send)(
                f'table_{table.number}',
                {
                    'type': 'product_availability',
                    'product_id': product.id,
                    'is_available': product.is_available,
                    'product_name': product.name,
                }
            )

        return Response({
            'id': product.id,
            'name': product.name,
            'is_available': product.is_available
        })


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsStaff()]
        return [IsAdmin()]


class RecipeItemViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeItemSerializer

    def get_queryset(self):
        qs = RecipeItem.objects.all()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsStaff()]
        return [IsAdmin()]


class StockReceiptViewSet(viewsets.ModelViewSet):
    queryset = StockReceipt.objects.all()
    serializer_class = StockReceiptSerializer
    permission_classes = [IsAdmin]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    permission_classes = [IsAdmin]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsStaff()]
        return [IsAdmin()]

class PurchaseInvoiceViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoice.objects.all().prefetch_related('items__ingredient').order_by('-date', '-created_at')
    serializer_class = PurchaseInvoiceSerializer
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        try:
            # Evitam mutarea directa a request.data
            data = dict(request.data)
            
            # Extragem lista de produse
            items_data = data.pop('items', [])

            # Cream factura
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            invoice = serializer.save()

            # Daca am asociat un furnizor relational, ne asiguram ca salvam si supplier_name
            if invoice.supplier and (not invoice.supplier_name or invoice.supplier_name != invoice.supplier.name):
                invoice.supplier_name = invoice.supplier.name
                invoice.save()

            # Cream liniile de receptie
            for item in items_data:
                unit_price = item.get('unit_price_without_vat')
                StockReceipt.objects.create(
                    invoice=invoice,
                    ingredient_id=item['ingredient'],
                    quantity=Decimal(str(item['quantity'])),
                    unit_price_without_vat=Decimal(str(unit_price)) if unit_price else None,
                    vat_rate=int(item.get('vat_rate', 9))
                )

            # Reincarcam cu related fields pentru response
            invoice_with_items = PurchaseInvoice.objects.prefetch_related('items__ingredient').get(id=invoice.id)
            
            from orders.models import log_operation
            log_operation(
                user=request.user,
                order=None,
                operation_type="Recepție Marfă (NIR)",
                description=f"A fost înregistrată factura de achiziție #{invoice.invoice_number} de la furnizorul '{invoice.supplier_name}', conținând {len(items_data)} linii de produse recepționate."
            )

            return Response(PurchaseInvoiceSerializer(invoice_with_items).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise e