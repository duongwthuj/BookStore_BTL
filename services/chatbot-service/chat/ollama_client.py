"""
Ollama API client for chatbot service.
"""
import requests
from django.conf import settings


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.system_prompt = settings.CHATBOT_SYSTEM_PROMPT
        self.generate_url = f"{self.base_url}/api/generate"

    def generate_response(self, user_message: str, context: str = None) -> dict:
        """
        Generate a response from Ollama.

        Args:
            user_message: The user's message/question
            context: Optional additional context to include in the prompt

        Returns:
            dict with 'success', 'response' or 'error' keys
        """
        # Build the prompt with system context
        prompt = f"{self.system_prompt}\n\n"

        if context:
            prompt += f"Thông tin bổ sung:\n{context}\n\n"

        prompt += f"Người dùng: {user_message}\nTrợ lý:"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=180  # Longer timeout for first model load
            )
            response.raise_for_status()

            data = response.json()
            return {
                "success": True,
                "response": data.get("response", "").strip(),
                "model": self.model,
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Ollama service timeout",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to Ollama service",
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Ollama request failed: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
            }

    def health_check(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


# Singleton instance
ollama_client = OllamaClient()
