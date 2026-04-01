"""
MoMo Payment Gateway Integration Module

This module handles all MoMo API interactions including:
- Creating payment requests
- Verifying signatures
- Processing callbacks
"""

import hashlib
import hmac
import json
import uuid
import requests
from django.conf import settings


class MoMoClient:
    """Client for MoMo Payment Gateway API"""

    def __init__(self):
        self.partner_code = settings.MOMO_PARTNER_CODE
        self.access_key = settings.MOMO_ACCESS_KEY
        self.secret_key = settings.MOMO_SECRET_KEY
        self.redirect_url = settings.MOMO_REDIRECT_URL
        self.ipn_url = settings.MOMO_IPN_URL
        self.endpoint = settings.MOMO_ENDPOINT

    def _generate_signature(self, raw_signature: str) -> str:
        """Generate HMAC SHA256 signature"""
        h = hmac.new(
            self.secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        )
        return h.hexdigest()

    def create_payment(self, order_id: int, amount: int, order_info: str = 'Payment') -> dict:
        """
        Create a MoMo payment request

        Args:
            order_id: The order ID from order-service
            amount: Payment amount in VND (must be integer)
            order_info: Description of the payment

        Returns:
            dict: MoMo API response containing payment URL or error
        """
        request_id = str(uuid.uuid4())
        momo_order_id = f"{self.partner_code}-{order_id}-{request_id[:8]}"
        request_type = "captureWallet"
        extra_data = ""

        # Build raw signature string according to MoMo specification
        raw_signature = (
            f"accessKey={self.access_key}"
            f"&amount={amount}"
            f"&extraData={extra_data}"
            f"&ipnUrl={self.ipn_url}"
            f"&orderId={momo_order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={self.partner_code}"
            f"&redirectUrl={self.redirect_url}"
            f"&requestId={request_id}"
            f"&requestType={request_type}"
        )

        signature = self._generate_signature(raw_signature)

        payload = {
            "partnerCode": self.partner_code,
            "partnerName": "E-Commerce Store",
            "storeId": self.partner_code,
            "requestId": request_id,
            "amount": amount,
            "orderId": momo_order_id,
            "orderInfo": order_info,
            "redirectUrl": self.redirect_url,
            "ipnUrl": self.ipn_url,
            "lang": "vi",
            "extraData": extra_data,
            "requestType": request_type,
            "signature": signature,
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'resultCode': -1,
                'message': f'Failed to connect to MoMo: {str(e)}'
            }

    def verify_callback_signature(self, callback_data: dict) -> bool:
        """
        Verify the signature from MoMo callback (IPN)

        Args:
            callback_data: The callback data from MoMo

        Returns:
            bool: True if signature is valid, False otherwise
        """
        received_signature = callback_data.get('signature', '')

        raw_signature = (
            f"accessKey={self.access_key}"
            f"&amount={callback_data.get('amount', '')}"
            f"&extraData={callback_data.get('extraData', '')}"
            f"&message={callback_data.get('message', '')}"
            f"&orderId={callback_data.get('orderId', '')}"
            f"&orderInfo={callback_data.get('orderInfo', '')}"
            f"&orderType={callback_data.get('orderType', '')}"
            f"&partnerCode={callback_data.get('partnerCode', '')}"
            f"&payType={callback_data.get('payType', '')}"
            f"&requestId={callback_data.get('requestId', '')}"
            f"&responseTime={callback_data.get('responseTime', '')}"
            f"&resultCode={callback_data.get('resultCode', '')}"
            f"&transId={callback_data.get('transId', '')}"
        )

        calculated_signature = self._generate_signature(raw_signature)
        return hmac.compare_digest(calculated_signature, received_signature)

    def parse_order_id(self, momo_order_id: str) -> int:
        """
        Parse original order ID from MoMo order ID

        Args:
            momo_order_id: The order ID format: PARTNER-ORDER_ID-UUID

        Returns:
            int: The original order ID
        """
        try:
            parts = momo_order_id.split('-')
            if len(parts) >= 2:
                return int(parts[1])
        except (ValueError, IndexError):
            pass
        return 0


# Singleton instance
momo_client = MoMoClient()
