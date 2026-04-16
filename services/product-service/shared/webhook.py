"""Notify chatbot-service when products change."""
import logging
import os
import threading

import requests

logger = logging.getLogger(__name__)

CHATBOT_SERVICE_URL = os.environ.get('CHATBOT_SERVICE_URL', 'http://chatbot-service:8000')
WEBHOOK_TIMEOUT = 5


def _send_webhook(action: str, product_data: dict = None, product_id: str = None):
    url = f"{CHATBOT_SERVICE_URL}/api/chat/webhook/book-updated/"
    payload = {"action": action}
    if product_data:
        payload["book"] = product_data
    if product_id:
        payload["book_id"] = str(product_id)

    def _do_send():
        try:
            response = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT)
            if response.status_code >= 300:
                logger.warning(f"Webhook failed ({response.status_code}): {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            logger.debug(f"Chatbot service unreachable, skipping webhook: {action}")
        except Exception as e:
            logger.warning(f"Webhook error: {e}")

    threading.Thread(target=_do_send, daemon=True).start()


def notify_product_created(product_data: dict):
    _send_webhook("created", product_data=product_data)


def notify_product_updated(product_data: dict):
    _send_webhook("updated", product_data=product_data)


def notify_product_deleted(product_id):
    _send_webhook("deleted", product_id=str(product_id))
