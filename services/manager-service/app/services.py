"""
Services for inter-service communication.
"""
import requests
from django.conf import settings


class OrderService:
    """Service client for order-service."""

    def __init__(self):
        self.base_url = settings.ORDER_SERVICE_URL

    def get_sales_statistics(self):
        """Get sales statistics from order-service."""
        try:
            response = requests.get(
                f"{self.base_url}/orders/statistics/sales/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "message": "Failed to fetch sales statistics"}

    def get_order_statistics(self):
        """Get order statistics from order-service."""
        try:
            response = requests.get(
                f"{self.base_url}/orders/statistics/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "message": "Failed to fetch order statistics"}


class StaffService:
    """Service client for staff-service."""

    def __init__(self):
        self.base_url = settings.STAFF_SERVICE_URL

    def get_staff_statistics(self):
        """Get staff statistics from staff-service."""
        try:
            response = requests.get(
                f"{self.base_url}/staff/statistics/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "message": "Failed to fetch staff statistics"}


# Service instances for easy import
order_service = OrderService()
staff_service = StaffService()
