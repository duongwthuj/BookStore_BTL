"""
RAG service - orchestrates the full retrieval-augmented generation pipeline.
"""
import logging
from typing import Dict, List, Optional

from .embedding_service import embedding_service
from .vector_store import vector_store
from .context_builder import context_builder
from .mongo_store import mongo_store
from .book_query import (
    detect_query_intent, fetch_for_intent, build_stats_summary, enrich_with_related_books,
)

logger = logging.getLogger(__name__)


class RAGService:
    """Main RAG orchestrator."""

    def query(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        top_k: int = None,
    ) -> Dict:
        """
        Run RAG pipeline: smart query detection -> embed -> search -> build context.
        """
        # 1. Conversation history
        conversation_history = []
        if session_id:
            try:
                conversation_history = mongo_store.get_recent_context(session_id)
            except Exception as e:
                logger.warning(f"Failed to get conversation history: {e}")

        # 2. Smart query: detect aggregation intent and fetch structured data
        structured_context = ""
        intent = detect_query_intent(user_message)
        if intent:
            structured_context = fetch_for_intent(intent)

        # 3. Always include store stats summary for factual grounding
        stats_summary = build_stats_summary()

        # 4. Embed the query and search vector store (semantic search)
        search_results = []
        try:
            query_embedding = embedding_service.embed_text(user_message)
            search_results = vector_store.search(
                query_embedding=query_embedding, top_k=top_k,
            )
            search_results = self._deduplicate(search_results)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")

        # 5. Build context from search results
        context_data = context_builder.build_context(search_results)

        # 6. KB-lite: enrich with related books if a specific book was found
        related_context = ""
        if search_results and not intent:
            try:
                related_context = enrich_with_related_books(search_results)
            except Exception as e:
                logger.warning(f"KB enrichment failed: {e}")

        # 7. Build final prompt with all context layers
        prompt = context_builder.build_chat_prompt(
            user_message=user_message,
            context_text=context_data["context_text"],
            structured_context=structured_context,
            related_context=related_context,
            stats_summary=stats_summary,
            conversation_history=conversation_history,
        )

        return {
            "context_text": context_data["context_text"],
            "sources": context_data["sources"],
            "avg_score": context_data["avg_score"],
            "conversation_history": conversation_history,
            "prompt": prompt,
        }

    def save_interaction(
        self,
        session_id: str,
        user_message: str,
        bot_response: str,
        sources: List[Dict] = None,
    ):
        """Save a chat interaction to MongoDB."""
        try:
            mongo_store.save_message(session_id, "user", user_message)
            mongo_store.save_message(session_id, "assistant", bot_response, sources=sources)
        except Exception as e:
            logger.error(f"Failed to save interaction: {e}")

    def _deduplicate(self, results: List[Dict], max_per_source: int = 2) -> List[Dict]:
        """Deduplicate results, keeping max N per source."""
        source_counts = {}
        deduped = []
        for result in results:
            source_id = result.get("metadata", {}).get("source_id", "unknown")
            count = source_counts.get(source_id, 0)
            if count < max_per_source:
                deduped.append(result)
                source_counts[source_id] = count + 1
        return deduped


rag_service = RAGService()
