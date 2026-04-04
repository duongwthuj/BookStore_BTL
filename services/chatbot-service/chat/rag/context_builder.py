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
        """
        Build context string from search results.

        Returns dict with 'context_text', 'sources', 'avg_score'.
        """
        if not search_results:
            return {
                "context_text": "",
                "sources": [],
                "avg_score": 0.0,
            }

        context_parts = []
        sources = []
        total_score = 0
        current_length = 0

        for i, result in enumerate(search_results):
            content = result.get("content", "")
            score = result.get("score", 0)
            metadata = result.get("metadata", {})

            # Check length limit
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
            # Only include optional fields if they have values
            for key in ("book_id", "author", "price"):
                val = metadata.get(key)
                if val:
                    source_entry[key] = val
            sources.append(source_entry)

            total_score += score

        context_text = "\n\n".join(context_parts)
        avg_score = total_score / len(sources) if sources else 0

        return {
            "context_text": context_text,
            "sources": sources,
            "avg_score": round(avg_score, 3),
        }

    def build_chat_prompt(
        self,
        user_message: str,
        context_text: str,
        conversation_history: List[Dict] = None,
    ) -> str:
        """Build the final prompt with RAG context and conversation history."""
        parts = []

        if context_text:
            parts.append(
                "Thông tin tham khảo từ cơ sở dữ liệu:\n"
                "---\n"
                f"{context_text}\n"
                "---"
            )

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
