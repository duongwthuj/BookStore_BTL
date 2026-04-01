"""
Service layer for external API calls.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OrderService:
    """Service to interact with the order-service."""

    def __init__(self):
        self.base_url = settings.ORDER_SERVICE_URL

    def verify_purchase(self, customer_id: int, book_id: int) -> bool:
        """
        Verify if a customer has purchased a specific book.

        Args:
            customer_id: The customer's ID
            book_id: The book's ID

        Returns:
            bool: True if the customer has purchased the book, False otherwise
        """
        if not customer_id:
            return False

        try:
            url = f"{self.base_url}/orders/verify-purchase/"
            params = {
                'customer_id': customer_id,
                'book_id': book_id,
            }
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return data.get('verified', False)

            logger.warning(
                f"Failed to verify purchase for customer {customer_id}, book {book_id}. "
                f"Status: {response.status_code}"
            )
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error verifying purchase: {e}")
            return False

    def get_customer_orders(self, customer_id: int) -> list:
        """
        Get all orders for a customer.

        Args:
            customer_id: The customer's ID

        Returns:
            list: List of orders
        """
        try:
            url = f"{self.base_url}/orders/"
            params = {'customer_id': customer_id}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                return response.json().get('results', [])

            return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting customer orders: {e}")
            return []


order_service = OrderService()
