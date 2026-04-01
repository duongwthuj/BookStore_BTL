from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CollectionViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'collections', CollectionViewSet, basename='collection')

urlpatterns = [
    path('', include(router.urls)),
]
