import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class OrderServiceClient:
    """Client for communicating with the order-service."""

    def __init__(self):
        self.base_url = settings.ORDER_SERVICE_URL

    def update_order_shipping_status(self, order_id: int, shipping_status: str) -> bool:
        """
        Notify order-service about shipping status changes.

        Args:
            order_id: The order ID to update
            shipping_status: The new shipping status

        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            url = f"{self.base_url}/orders/{order_id}/shipping-status/"
            payload = {
                'shipping_status': shipping_status
            }
            response = requests.put(url, json=payload, timeout=10)

            if response.status_code in (200, 204):
                logger.info(f"Successfully updated order {order_id} shipping status to {shipping_status}")
                return True
            else:
                logger.warning(
                    f"Failed to update order {order_id} shipping status. "
                    f"Status code: {response.status_code}, Response: {response.text}"
                )
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with order-service for order {order_id}: {str(e)}")
            return False

    def get_order_details(self, order_id: int) -> dict | None:
        """
        Get order details from order-service.

        Args:
            order_id: The order ID to retrieve

        Returns:
            dict: Order details if found, None otherwise
        """
        try:
            url = f"{self.base_url}/orders/{order_id}/"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    f"Failed to get order {order_id}. "
                    f"Status code: {response.status_code}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting order {order_id} from order-service: {str(e)}")
            return None


order_service_client = OrderServiceClient()
