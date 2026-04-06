"""
OpenAI API client for chatbot service.
"""
import requests
from django.conf import settings


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.system_prompt = settings.CHATBOT_SYSTEM_PROMPT
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_response(self, user_message: str, context: str = None) -> dict:
        """
        Generate a response from OpenAI.

        Args:
            user_message: The user's message/question
            context: Optional additional context to include in the prompt

        Returns:
            dict with 'success', 'response' or 'error' keys
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
            }

        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        if context:
            messages.append({"role": "system", "content": f"Thông tin bổ sung:\n{context}"})

        messages.append({"role": "user", "content": user_message})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid OpenAI API key",
                }

            if response.status_code == 429:
                return {
                    "success": False,
                    "error": "OpenAI rate limit exceeded",
                }

            response.raise_for_status()

            data = response.json()
            choices = data.get("choices", [])
            if choices:
                response_text = choices[0].get("message", {}).get("content", "").strip()
                return {
                    "success": True,
                    "response": response_text,
                    "model": self.model,
                }

            return {
                "success": False,
                "error": "Empty response from OpenAI",
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "OpenAI service timeout",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to OpenAI service",
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"OpenAI request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }

    def health_check(self) -> bool:
        """Check if OpenAI API is available."""
        return bool(self.api_key)


# Singleton instance
openai_client = OpenAIClient()
