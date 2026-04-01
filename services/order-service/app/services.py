"""
Services for inter-service communication with cart-service and book-service.
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CartServiceClient:
    """Client for communicating with cart-service."""

    def __init__(self):
        self.base_url = settings.CART_SERVICE_URL

    def get_cart(self, customer_id):
        """Get cart for a customer."""
        try:
            response = requests.get(
                f"{self.base_url}/cart/{customer_id}/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching cart for customer {customer_id}: {e}")
            raise ServiceException(f"Failed to fetch cart: {e}")

    def clear_cart(self, customer_id):
        """Clear cart after successful order."""
        try:
            response = requests.delete(
                f"{self.base_url}/cart/{customer_id}/clear/",
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error clearing cart for customer {customer_id}: {e}")
            # Don't raise exception - cart clearing is not critical
            return False


class BookServiceClient:
    """Client for communicating with book-service."""

    def __init__(self):
        self.base_url = settings.BOOK_SERVICE_URL

    def get_book(self, book_id):
        """Get book details."""
        try:
            response = requests.get(
                f"{self.base_url}/books/{book_id}/",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            raise ServiceException(f"Failed to fetch book: {e}")

    def update_stock(self, book_id, quantity_change):
        """
        Update book stock.
        quantity_change: negative for decrease, positive for increase
        """
        try:
            response = requests.patch(
                f"{self.base_url}/books/{book_id}/stock/",
                json={"quantity_change": quantity_change},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error updating stock for book {book_id}: {e}")
            raise ServiceException(f"Failed to update stock: {e}")

    def check_stock(self, book_id, quantity):
        """Check if book has enough stock."""
        try:
            book = self.get_book(book_id)
            stock = book.get('stock', 0)
            return stock >= quantity
        except ServiceException:
            return False

    def bulk_update_stock(self, items):
        """
        Update stock for multiple books.
        items: list of dicts with book_id and quantity
        """
        results = []
        for item in items:
            try:
                result = self.update_stock(
                    item['book_id'],
                    -item['quantity']  # Decrease stock
                )
                results.append({
                    'book_id': item['book_id'],
                    'success': True,
                    'result': result
                })
            except ServiceException as e:
                results.append({
                    'book_id': item['book_id'],
                    'success': False,
                    'error': str(e)
                })
        return results


class ServiceException(Exception):
    """Exception raised when service communication fails."""
    pass


# Singleton instances
cart_service = CartServiceClient()
book_service = BookServiceClient()
