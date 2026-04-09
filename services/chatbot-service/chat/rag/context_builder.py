"""
Context builder for constructing RAG prompts from search results.
"""
from typing import Dict, List


class ContextBuilder:
    """Build LLM context from RAG search results."""

    def build_context(
        self,
        search_results: List[Dict],
        max_length: int = 4000,
    ) -> Dict:
        """Build context string from vector search results."""
        if not search_results:
            return {"context_text": "", "sources": [], "avg_score": 0.0}

        context_parts = []
        sources = []
        total_score = 0
        current_length = 0

        for i, result in enumerate(search_results):
            content = result.get("content", "")
            score = result.get("score", 0)
            metadata = result.get("metadata", {})

            if current_length + len(content) > max_length:
                remaining = max_length - current_length
                if remaining > 100:
                    content = content[:remaining]
                else:
                    break

            source_title = metadata.get("source_title", f"Nguồn {i + 1}")
            context_parts.append(f"[{source_title}]\n{content}")
            current_length += len(content) + len(source_title) + 4

            source_entry = {
                "title": source_title,
                "score": round(score, 3),
                "source_type": metadata.get("source_type", "unknown"),
            }
            for key in ("book_id", "author", "price"):
                val = metadata.get(key)
                if val:
                    source_entry[key] = val
            sources.append(source_entry)
            total_score += score

        return {
            "context_text": "\n\n".join(context_parts),
            "sources": sources,
            "avg_score": round(total_score / len(sources), 3) if sources else 0,
        }

    def build_chat_prompt(
        self,
        user_message: str,
        context_text: str,
        structured_context: str = "",
        related_context: str = "",
        stats_summary: str = "",
        conversation_history: List[Dict] = None,
    ) -> str:
        """Build the final prompt combining all context layers."""
        parts = []

        # Stats summary (always present — factual grounding)
        if stats_summary:
            parts.append(stats_summary)

        # Structured data from smart query (aggregations, sorting)
        if structured_context:
            parts.append(f"[Dữ liệu chính xác từ hệ thống]\n{structured_context}")

        # RAG vector search results
        if context_text:
            parts.append(
                "Thông tin tham khảo từ cơ sở dữ liệu:\n"
                f"---\n{context_text}\n---"
            )

        # KB-lite: related books (same author, same category)
        if related_context:
            parts.append(f"[Sách liên quan gợi ý]\n{related_context}")

        # Conversation history (last 6 messages)
        if conversation_history:
            history_text = []
            for msg in conversation_history[-6:]:
                role = "Khách hàng" if msg["role"] == "user" else "Trợ lý"
                history_text.append(f"{role}: {msg['content']}")
            if history_text:
                parts.append(
                    "Lịch sử hội thoại gần đây:\n" + "\n".join(history_text)
                )

        parts.append(f"Khách hàng: {user_message}")
        return "\n\n".join(parts)


context_builder = ContextBuilder()
