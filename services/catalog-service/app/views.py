from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Category, Collection
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CollectionSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations.

    list: Returns categories in nested structure (only root categories with children)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        # For list action, only return root categories (parent=None)
        # Children will be nested in the serializer
        if self.action == 'list':
            queryset = queryset.filter(parent__isnull=True)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Set children's parent to None before deleting
        instance.children.update(parent=None)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Collection CRUD operations.
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
