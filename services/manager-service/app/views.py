from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Manager
from .serializers import ManagerSerializer
from .services import order_service, staff_service


class ManagerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Manager CRUD operations.
    """
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get manager by user_id."""
        manager = get_object_or_404(Manager, user_id=user_id)
        serializer = self.get_serializer(manager)
        return Response(serializer.data)


class DashboardSalesView(APIView):
    """
    Dashboard endpoint for sales statistics.
    Calls order-service to get sales data.
    """
    def get(self, request):
        data = order_service.get_sales_statistics()
        return Response(data)


class DashboardStaffView(APIView):
    """
    Dashboard endpoint for staff statistics.
    Calls staff-service to get staff data.
    """
    def get(self, request):
        data = staff_service.get_staff_statistics()
        return Response(data)


class DashboardOrdersView(APIView):
    """
    Dashboard endpoint for order statistics.
    Calls order-service to get order data.
    """
    def get(self, request):
        data = order_service.get_order_statistics()
        return Response(data)
