"""
Google Gemini API client for chatbot service.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.system_prompt = settings.CHATBOT_SYSTEM_PROMPT

    @property
    def api_url(self):
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_response(self, user_message: str, context: str = None) -> dict:
        """Generate a response from Gemini."""
        if not self.api_key:
            return {"success": False, "error": "Gemini API key not configured"}

        prompt = f"{self.system_prompt}\n\n"
        if context:
            prompt += f"Thông tin bổ sung:\n{context}\n\n"
        prompt += f"Người dùng: {user_message}\nTrợ lý:"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            },
        }

        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=30,
            )

            if response.status_code == 429:
                return {"success": False, "error": "Gemini rate limit exceeded, vui lòng thử lại sau"}
            if response.status_code == 400:
                return {"success": False, "error": "Invalid request to Gemini API"}
            if response.status_code == 403:
                return {"success": False, "error": "Invalid Gemini API key"}

            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return {
                        "success": True,
                        "response": parts[0].get("text", "").strip(),
                        "model": self.model,
                    }

            return {"success": False, "error": "Empty response from Gemini"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Gemini service timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to Gemini service"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Gemini request failed: {str(e)}"}

    def health_check(self) -> bool:
        return bool(self.api_key)


gemini_client = GeminiClient()
