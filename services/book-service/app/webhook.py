"""
Webhook client to notify chatbot-service when books change.
Fires asynchronously so book CRUD is never blocked by chatbot availability.
"""
import logging
import os
import threading

import requests

logger = logging.getLogger(__name__)

CHATBOT_SERVICE_URL = os.environ.get(
    'CHATBOT_SERVICE_URL', 'http://chatbot-service:8000'
)
WEBHOOK_TIMEOUT = 5  # seconds


def _send_webhook(action: str, book_data: dict = None, book_id: str = None):
    """Send webhook notification to chatbot-service in a background thread."""
    url = f"{CHATBOT_SERVICE_URL}/api/chat/webhook/book-updated/"
    payload = {"action": action}

    if book_data:
        payload["book"] = book_data
    if book_id:
        payload["book_id"] = str(book_id)

    def _do_send():
        try:
            response = requests.post(url, json=payload, timeout=WEBHOOK_TIMEOUT)
            if response.status_code < 300:
                logger.info(f"Webhook sent: {action} book_id={book_id or book_data.get('id')}")
            else:
                logger.warning(
                    f"Webhook failed ({response.status_code}): {response.text[:200]}"
                )
        except requests.exceptions.ConnectionError:
            logger.debug(f"Chatbot service unreachable, skipping webhook: {action}")
        except Exception as e:
            logger.warning(f"Webhook error: {e}")

    thread = threading.Thread(target=_do_send, daemon=True)
    thread.start()


def notify_book_created(book_data: dict):
    _send_webhook("created", book_data=book_data)


def notify_book_updated(book_data: dict):
    _send_webhook("updated", book_data=book_data)


def notify_book_deleted(book_id):
    _send_webhook("deleted", book_id=str(book_id))
