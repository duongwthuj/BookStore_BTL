"""
Embedding service using HuggingFace SentenceTransformers.
Optimized for Vietnamese text with dangvantuan/vietnamese-document-embedding.
"""
import logging
import os
import ssl
import threading
from typing import List

from django.conf import settings

# Fix SSL certificate issue on macOS development (system Python 3.9)
# In Docker production, Python has proper certificates installed
try:
    import certifi
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    os.environ.setdefault('REQUESTS_CA_BUNDLE', certifi.where())
except ImportError:
    pass

try:
    ssl._create_default_https_context = ssl._create_unverified_context
    import urllib3.util.ssl_
    _orig_create_ctx = urllib3.util.ssl_.create_urllib3_context

    def _patched_create_ctx(**kwargs):
        ctx = _orig_create_ctx(**kwargs)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    urllib3.util.ssl_.create_urllib3_context = _patched_create_ctx
except Exception:
    pass

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using SentenceTransformers."""

    def __init__(self):
        self._model = None
        self._lock = threading.Lock()
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    @property
    def model(self):
        if self._model is None:
            with self._lock:
                # Double-check after acquiring lock
                if self._model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                        self._model = SentenceTransformer(self.model_name, trust_remote_code=True)
                        logger.info(f"Loaded embedding model: {self.model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load embedding model: {e}")
                        raise
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embed a batch of texts."""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(batch, normalize_embeddings=True)
            all_embeddings.extend(embeddings.tolist())
        return all_embeddings

    def health_check(self) -> bool:
        try:
            self.embed_text("test")
            return True
        except Exception:
            return False


embedding_service = EmbeddingService()
