from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ManagerViewSet,
    DashboardSalesView,
    DashboardStaffView,
    DashboardOrdersView,
)

router = DefaultRouter()
router.register(r'managers', ManagerViewSet, basename='manager')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/sales/', DashboardSalesView.as_view(), name='dashboard-sales'),
    path('dashboard/staff/', DashboardStaffView.as_view(), name='dashboard-staff'),
    path('dashboard/orders/', DashboardOrdersView.as_view(), name='dashboard-orders'),
]
