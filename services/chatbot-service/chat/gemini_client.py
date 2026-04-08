"""
Google Gemini API client for chatbot service.
"""
import requests
from django.conf import settings


class GeminiClient:
    """Client for interacting with Google Gemini API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.system_prompt = settings.CHATBOT_SYSTEM_PROMPT
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_response(self, user_message: str, context: str = None) -> dict:
        """
        Generate a response from Gemini.

        Args:
            user_message: The user's message/question
            context: Optional additional context to include in the prompt

        Returns:
            dict with 'success', 'response' or 'error' keys
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Gemini API key not configured",
            }

        # Build the prompt with system context
        prompt = f"{self.system_prompt}\n\n"

        if context:
            prompt += f"Thông tin bổ sung:\n{context}\n\n"

        prompt += f"Người dùng: {user_message}\nTrợ lý:"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=30
            )

            if response.status_code == 400:
                return {
                    "success": False,
                    "error": "Invalid request to Gemini API",
                }

            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "Invalid Gemini API key",
                }

            response.raise_for_status()

            data = response.json()

            # Extract response text from Gemini response structure
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    response_text = parts[0].get("text", "").strip()
                    return {
                        "success": True,
                        "response": response_text,
                        "model": self.model,
                    }

            return {
                "success": False,
                "error": "Empty response from Gemini",
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Gemini service timeout",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to Gemini service",
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Gemini request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }

    def health_check(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key)


# Singleton instance
gemini_client = GeminiClient()
