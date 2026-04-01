from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet,
    BookSearchView,
    BooksByCategoryView,
    BooksByCollectionView,
)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('books/search/', BookSearchView.as_view(), name='book-search'),
    path('books/category/<int:category_id>/', BooksByCategoryView.as_view(), name='books-by-category'),
    path('books/collection/<int:collection_id>/', BooksByCollectionView.as_view(), name='books-by-collection'),
    path('', include(router.urls)),
]
