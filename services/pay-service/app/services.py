"""
Service layer for payment operations

This module handles:
- Payment business logic
- Communication with order-service
- Payment status management
"""

import logging
import requests
from django.conf import settings
from django.utils import timezone
from .models import Payment

logger = logging.getLogger(__name__)


class OrderServiceClient:
    """Client for communicating with order-service"""

    def __init__(self):
        self.base_url = settings.ORDER_SERVICE_URL.rstrip('/')

    def _url(self, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        return f"{self.base_url}{path}"

    def get_order(self, order_id: int) -> dict:
        """
        Fetch order details from order-service

        Args:
            order_id: The order ID

        Returns:
            dict: Order details or None if not found
        """
        try:
            response = requests.get(
                self._url(f"/api/orders/{order_id}/"),
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch order {order_id}: {e}")
        return None

    def update_order_status(self, order_id: int, new_status: str) -> bool:
        """
        Update order status in order-service.

        order-service exposes: PUT /api/orders/{id}/status/ {"status": "paid"}

        Args:
            order_id: The order ID
            new_status: New order status (e.g. 'paid')

        Returns:
            bool: True if update successful
        """
        try:
            payload = {'status': new_status}
            response = requests.put(
                self._url(f"/api/orders/{order_id}/status/"),
                json=payload,
                timeout=10,
            )
            return response.status_code in (200, 204)
        except requests.RequestException as e:
            logger.error(f"Failed to update order {order_id} status to {new_status}: {e}")
        return False


class PaymentService:
    """Service class for payment operations"""

    def __init__(self):
        self.order_client = OrderServiceClient()

    def create_momo_payment(self, order_id: int, amount: float, order_info: str = 'Payment') -> Payment:
        """
        Create a new MoMo payment record

        Args:
            order_id: The order ID
            amount: Payment amount
            order_info: Payment description

        Returns:
            Payment: The created payment instance
        """
        # Check if payment already exists for this order
        existing = Payment.objects.filter(
            order_id=order_id,
            method='momo',
            status__in=['pending', 'success']
        ).first()

        if existing:
            if existing.status == 'success':
                raise ValueError('Payment already completed for this order')
            return existing

        payment = Payment.objects.create(
            order_id=order_id,
            method='momo',
            amount=amount,
            status='pending'
        )
        return payment

    def create_cod_payment(self, order_id: int, amount: float) -> Payment:
        """
        Create a new COD payment record

        Args:
            order_id: The order ID
            amount: Payment amount

        Returns:
            Payment: The created payment instance
        """
        # Check if payment already exists for this order
        existing = Payment.objects.filter(
            order_id=order_id,
            status__in=['pending', 'success']
        ).first()

        if existing:
            if existing.status == 'success':
                raise ValueError('Payment already completed for this order')
            return existing

        payment = Payment.objects.create(
            order_id=order_id,
            method='cod',
            amount=amount,
            status='pending'
        )

        return payment

    def process_momo_callback(self, order_id: int, result_code: int, transaction_id: str) -> Payment:
        """
        Process MoMo payment callback

        Args:
            order_id: The order ID
            result_code: MoMo result code (0 = success)
            transaction_id: MoMo transaction ID

        Returns:
            Payment: Updated payment instance
        """
        payment = Payment.objects.filter(
            order_id=order_id,
            method='momo',
            status='pending'
        ).first()

        if not payment:
            raise ValueError(f'No pending MoMo payment found for order {order_id}')

        if result_code == 0:
            payment.status = 'success'
            payment.transaction_id = str(transaction_id)
            payment.paid_at = timezone.now()
            self.order_client.update_order_status(order_id, 'paid')
        else:
            payment.status = 'failed'

        payment.save()
        return payment

    def confirm_cod_payment(self, order_id: int) -> Payment:
        """
        Confirm COD payment (called by staff when payment received)

        Args:
            order_id: The order ID

        Returns:
            Payment: Updated payment instance
        """
        payment = Payment.objects.filter(
            order_id=order_id,
            method='cod',
            status='pending'
        ).first()

        if not payment:
            raise ValueError(f'No pending COD payment found for order {order_id}')

        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.save()

        # Notify order-service
        self.order_client.update_order_status(order_id, 'paid')

        return payment

    def get_payment_by_order(self, order_id: int) -> Payment:
        """
        Get payment by order ID

        Args:
            order_id: The order ID

        Returns:
            Payment: Payment instance or None
        """
        return Payment.objects.filter(order_id=order_id).order_by('-created_at').first()


# Singleton instance
payment_service = PaymentService()
