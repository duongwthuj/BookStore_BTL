"""
External service integrations for chatbot.
"""
import requests
from django.conf import settings


class BookService:
    """Service to interact with book-service."""

    def __init__(self):
        self.base_url = settings.BOOK_SERVICE_URL

    def search_books(self, query: str) -> dict:
        """
        Search for books by query.

        Args:
            query: Search term (title, author, etc.)

        Returns:
            dict with 'success', 'books' or 'error' keys
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/books/",
                params={"search": query},
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            books = data.get("results", data) if isinstance(data, dict) else data

            return {
                "success": True,
                "books": books if isinstance(books, list) else [],
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Book service timeout",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to book service",
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Book service request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }


class OrderService:
    """Service to interact with order-service."""

    def __init__(self):
        self.base_url = settings.ORDER_SERVICE_URL

    def get_order_status(self, order_id: str) -> dict:
        """
        Get order status by order ID.

        Args:
            order_id: The order ID to look up

        Returns:
            dict with 'success', 'order' or 'error' keys
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/orders/{order_id}/",
                timeout=10
            )

            if response.status_code == 404:
                return {
                    "success": False,
                    "error": "Order not found",
                }

            response.raise_for_status()

            return {
                "success": True,
                "order": response.json(),
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Order service timeout",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to order service",
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Order service request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }


# Service instances
book_service = BookService()
order_service = OrderService()
