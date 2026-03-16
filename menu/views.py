from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsAdmin, IsBarman, IsKitchen, IsStaff
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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