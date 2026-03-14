from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsAdmin, IsBarman, IsKitchen
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


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
            return [IsBarman() if self._is_bar_product() else IsKitchen()]
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
        return Response({
            'id': product.id,
            'name': product.name,
            'is_available': product.is_available
        })