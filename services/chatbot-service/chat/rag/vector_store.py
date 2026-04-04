"""
Qdrant vector store for document storage and similarity search.
"""
import logging
import uuid
from typing import Dict, List, Optional

from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    FilterSelector,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

logger = logging.getLogger(__name__)


class VectorStore:
    """Qdrant-backed vector store for RAG."""

    def __init__(self):
        self._client = None
        self.collection_name = settings.QDRANT_COLLECTION
        self.dimension = settings.EMBEDDING_DIMENSION

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
            self._ensure_collection()
        return self._client

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self._client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self._client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    def upsert_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
    ) -> List[str]:
        """Insert or update documents in the vector store."""
        points = []
        point_ids = []
        for text, embedding, metadata in zip(texts, embeddings, metadatas):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)
            payload = {
                "content": text,
                **metadata,
            }
            points.append(PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload,
            ))

        # Batch upsert (100 at a time)
        for i in range(0, len(points), 100):
            batch = points[i:i + 100]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        logger.info(f"Upserted {len(points)} points to Qdrant")
        return point_ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = None,
        score_threshold: float = None,
        source_filter: Optional[str] = None,
    ) -> List[Dict]:
        """Search for similar documents."""
        top_k = top_k or settings.RAG_TOP_K
        score_threshold = score_threshold or settings.RAG_SIMILARITY_THRESHOLD

        query_filter = None
        if source_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="source_type",
                        match=MatchValue(value=source_filter),
                    )
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )

        return [
            {
                "id": str(hit.id),
                "content": hit.payload.get("content", ""),
                "score": hit.score,
                "metadata": {
                    k: v for k, v in hit.payload.items() if k != "content"
                },
            }
            for hit in results
        ]

    def delete_by_source(self, source_id: str):
        """Delete all points from a specific source."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="source_id",
                            match=MatchValue(value=source_id),
                        )
                    ]
                )
            ),
        )
        logger.info(f"Deleted points for source: {source_id}")

    def get_collection_info(self) -> Dict:
        """Get collection statistics."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status.value,
            }
        except Exception as e:
            return {"error": str(e)}

    def health_check(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False


vector_store = VectorStore()
