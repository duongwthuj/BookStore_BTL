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


# Singleton instance
book_service = BookService()
