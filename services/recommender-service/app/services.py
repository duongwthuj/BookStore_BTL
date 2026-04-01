"""
Service layer for external API calls.
"""

import logging
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class BookServiceClient:
    """Client for communicating with the book-service."""

    def __init__(self):
        self.base_url = settings.BOOK_SERVICE_URL.rstrip('/')
        self.timeout = 10

    def get_book(self, book_id: int) -> Optional[dict]:
        """Fetch a single book by ID."""
        try:
            response = requests.get(
                f"{self.base_url}/books/{book_id}/",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Book {book_id} not found: {response.status_code}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching book {book_id}: {e}")
            return None

    def get_books(self, book_ids: list[int]) -> dict[int, dict]:
        """Fetch multiple books by their IDs."""
        books = {}
        for book_id in book_ids:
            book = self.get_book(book_id)
            if book:
                books[book_id] = book
        return books

    def get_books_by_category(self, category_id: int, limit: int = 20) -> list[dict]:
        """Fetch books by category."""
        try:
            response = requests.get(
                f"{self.base_url}/books/",
                params={'category': category_id, 'page_size': limit},
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('results', data) if isinstance(data, dict) else data
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching books by category {category_id}: {e}")
            return []

    def get_books_by_author(self, author_id: int, limit: int = 20) -> list[dict]:
        """Fetch books by author."""
        try:
            response = requests.get(
                f"{self.base_url}/books/",
                params={'author': author_id, 'page_size': limit},
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('results', data) if isinstance(data, dict) else data
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching books by author {author_id}: {e}")
            return []

    def get_all_books(self, limit: int = 100) -> list[dict]:
        """Fetch all books (for similarity computation)."""
        try:
            response = requests.get(
                f"{self.base_url}/books/",
                params={'page_size': limit},
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('results', data) if isinstance(data, dict) else data
            return []
        except requests.RequestException as e:
            logger.error(f"Error fetching all books: {e}")
            return []


book_service = BookServiceClient()
