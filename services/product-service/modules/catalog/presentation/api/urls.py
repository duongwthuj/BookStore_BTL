from django.urls import path, include
from rest_framework.routers import DefaultRouter
from modules.catalog.presentation.api.views.product_view import (
    ProductViewSet, ProductSearchView, ProductsByCategoryView, ProductsByCollectionView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/category/<int:category_id>/', ProductsByCategoryView.as_view(), name='products-by-category'),
    path('products/collection/<int:collection_id>/', ProductsByCollectionView.as_view(), name='products-by-collection'),
    path('', include(router.urls)),
]
