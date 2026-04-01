"""
Service layer for external service communication.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CartServiceClient:
    """Client for communicating with the cart-service."""

    def __init__(self):
        self.base_url = settings.CART_SERVICE_URL

    def create_cart(self, customer_id: int) -> dict | None:
        """
        Create a cart for a customer in the cart-service.

        Args:
            customer_id: The ID of the customer to create a cart for.

        Returns:
            The created cart data if successful, None otherwise.
        """
        url = f"{self.base_url}/carts/"
        payload = {"customer_id": customer_id}

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully created cart for customer {customer_id}")
            return response.json()
        except requests.exceptions.ConnectionError:
            logger.warning(
                f"Could not connect to cart-service at {url}. "
                f"Cart creation for customer {customer_id} skipped."
            )
            return None
        except requests.exceptions.Timeout:
            logger.warning(
                f"Timeout connecting to cart-service. "
                f"Cart creation for customer {customer_id} skipped."
            )
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP error creating cart for customer {customer_id}: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error creating cart for customer {customer_id}: {e}"
            )
            return None


cart_service_client = CartServiceClient()
