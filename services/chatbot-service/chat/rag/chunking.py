"""
Text chunking strategies for document processing.
"""
import logging
from typing import List, Dict

from django.conf import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """Split text into chunks for embedding."""

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.min_chunk_size = settings.MIN_CHUNK_SIZE

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks using recursive character splitting.

        Returns list of dicts with 'content' and 'metadata' keys.
        """
        metadata = metadata or {}

        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", ", ", " "],
                length_function=len,
            )
            chunks_text = splitter.split_text(text)
        except ImportError:
            # Fallback: simple splitting
            chunks_text = self._simple_split(text)

        chunks = []
        for i, chunk_content in enumerate(chunks_text):
            if len(chunk_content.strip()) < self.min_chunk_size:
                continue
            chunks.append({
                "content": chunk_content.strip(),
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks_text),
                },
            })

        logger.info(f"Split text into {len(chunks)} chunks (from {len(text)} chars)")
        return chunks

    def _simple_split(self, text: str) -> List[str]:
        """Fallback simple split by fixed size with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        return chunks


text_chunker = TextChunker()
