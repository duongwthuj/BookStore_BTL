from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from modules.catalog.infrastructure.models.product_model import ProductModel
from modules.catalog.infrastructure.repositories.product_repository_impl import DjangoProductRepository
from modules.catalog.application.services.product_service import ProductService
from modules.catalog.application.commands.create_product import CreateProductCommand
from modules.catalog.application.commands.update_product import UpdateProductCommand
from modules.catalog.application.commands.update_stock import UpdateStockCommand
from modules.catalog.application.queries.get_product import GetProductQuery
from modules.catalog.presentation.api.serializers.product_serializer import (
    ProductSerializer, ProductListSerializer, StockUpdateSerializer
)
from modules.catalog.presentation.api.filters.product_filter import ProductFilter
from shared.exceptions import ProductNotFoundError
from shared.webhook import notify_product_created, notify_product_updated, notify_product_deleted


def _get_service() -> ProductService:
    return ProductService(DjangoProductRepository())


class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.all()
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'author', 'description']
    ordering_fields = ['title', 'author', 'price', 'created_at', 'stock']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        command = CreateProductCommand(
            title=data['title'],
            author=data['author'],
            price=data['price'],
            stock=data.get('stock', 0),
            category_id=data['category_id'],
            description=data.get('description', ''),
            collection_ids=data.get('collection_ids', []),
            attributes=data.get('attributes', {}),
            cover_image=data.get('cover_image'),
        )
        service = _get_service()
        product = service.create_product(command)
        serializer.instance = ProductModel.objects.get(pk=product.id)
        notify_product_created(ProductSerializer(serializer.instance).data)

    def perform_update(self, serializer):
        data = serializer.validated_data
        command = UpdateProductCommand(
            product_id=serializer.instance.id,
            title=data.get('title'),
            author=data.get('author'),
            price=data.get('price'),
            stock=data.get('stock'),
            category_id=data.get('category_id'),
            description=data.get('description'),
            collection_ids=data.get('collection_ids'),
            attributes=data.get('attributes'),
            cover_image=data.get('cover_image'),
        )
        service = _get_service()
        product = service.update_product(command)
        serializer.instance = ProductModel.objects.get(pk=product.id)
        notify_product_updated(ProductSerializer(serializer.instance).data)

    def perform_destroy(self, instance):
        product_id = instance.id
        service = _get_service()
        service.delete_product(product_id)
        notify_product_deleted(product_id)

    @action(detail=True, methods=['put'], url_path='stock')
    def update_stock(self, request, pk=None):
        serializer = StockUpdateSerializer(data=request.data)
        if serializer.is_valid():
            command = UpdateStockCommand(
                product_id=int(pk),
                stock=serializer.validated_data['stock'],
            )
            service = _get_service()
            try:
                product = service.update_stock(command)
                model = ProductModel.objects.get(pk=product.id)
                return Response(ProductSerializer(model).data)
            except ProductNotFoundError as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query "q" is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        products = ProductModel.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            return paginator.get_paginated_response(ProductListSerializer(page, many=True).data)
        return Response(ProductListSerializer(products, many=True).data)


class ProductsByCategoryView(APIView):
    def get(self, request, category_id):
        products = ProductModel.objects.filter(category_id=category_id)
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            return paginator.get_paginated_response(ProductListSerializer(page, many=True).data)
        return Response(ProductListSerializer(products, many=True).data)


class ProductsByCollectionView(APIView):
    def get(self, request, collection_id):
        products = ProductModel.objects.filter(collection_ids__contains=[collection_id])
        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            return paginator.get_paginated_response(ProductListSerializer(page, many=True).data)
        return Response(ProductListSerializer(products, many=True).data)
