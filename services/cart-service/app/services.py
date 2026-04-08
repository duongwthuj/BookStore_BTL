"""
Service layer for external API calls.
"""

import requests
from django.conf import settings


class BookServiceError(Exception):
    """Exception raised when book service call fails."""
    pass


class BookService:
    """Service for interacting with the book-service."""

    def __init__(self):
        self.base_url = settings.BOOK_SERVICE_URL

    def get_book(self, book_id: int) -> dict:
        """
        Fetch book details from book-service.

        Args:
            book_id: The ID of the book to fetch.

        Returns:
            dict: Book data including id, title, price, etc.

        Raises:
            BookServiceError: If the book is not found or service is unavailable.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/books/{book_id}/",
                timeout=5
            )
            if response.status_code == 404:
                raise BookServiceError(f"Book with id {book_id} not found")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise BookServiceError("Book service is unavailable")
        except requests.exceptions.Timeout:
            raise BookServiceError("Book service request timed out")
        except requests.exceptions.RequestException as e:
            raise BookServiceError(f"Error fetching book: {str(e)}")

    def get_book_price(self, book_id: int) -> float:
        """
        Get the current price of a book.

        Args:
            book_id: The ID of the book.

        Returns:
            float: The price of the book.

        Raises:
            BookServiceError: If the book is not found or service is unavailable.
        """
        book = self.get_book(book_id)
        return float(book.get('price', 0))

    def check_book_availability(self, book_id: int, quantity: int = 1) -> bool:
        """
        Check if a book is available in the requested quantity.

        Args:
            book_id: The ID of the book.
            quantity: The requested quantity.

        Returns:
            bool: True if available, False otherwise.
        """
        try:
            book = self.get_book(book_id)
            stock = book.get('stock', 0)
            return stock >= quantity
        except BookServiceError:
            return False


class RecommenderService:
    """Service for interacting with the recommender-service."""

    def __init__(self):
        self.base_url = getattr(settings, 'RECOMMENDER_SERVICE_URL', 'http://recommender-service:8000')

    def record_cart_interaction(self, customer_id: int, book_id: int):
        """Record an add-to-cart interaction."""
        try:
            response = requests.post(
                f"{self.base_url}/interactions/",
                json={
                    'customer_id': customer_id,
                    'book_id': book_id,
                    'interaction_type': 'cart'
                },
                timeout=3
            )
            return response.status_code == 201
        except requests.exceptions.RequestException:
            # Don't fail cart operation if recommender is down
            return False


# Singleton instances
book_service = BookService()
recommender_service = RecommenderService()
