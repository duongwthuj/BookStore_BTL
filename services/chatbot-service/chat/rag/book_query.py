"""
Smart book query module — fetches structured data from book-service API
for questions that RAG vector search can't answer well (counts, sorting, stats).
"""
import logging
import re
from typing import Dict, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Patterns that signal an aggregation/structured query
_PATTERNS = {
    "most_expensive": re.compile(
        r"(đắt nhất|giá cao nhất|mắc nhất|expensive)", re.IGNORECASE
    ),
    "cheapest": re.compile(
        r"(rẻ nhất|giá thấp nhất|giá rẻ|cheapest)", re.IGNORECASE
    ),
    "newest": re.compile(
        r"(mới nhất|mới ra|ra mắt gần đây|newest|latest)", re.IGNORECASE
    ),
    "count": re.compile(
        r"(bao nhiêu cuốn|bao nhiêu sách|bao nhiêu quyển|tổng.*sách|có mấy|tất cả.*sách"
        r"|how many books|total books)", re.IGNORECASE
    ),
    "in_stock": re.compile(
        r"(còn hàng|còn bán|available|in.?stock)", re.IGNORECASE
    ),
    "out_of_stock": re.compile(
        r"(hết hàng|out.?of.?stock)", re.IGNORECASE
    ),
}


def detect_query_intent(message: str) -> Optional[str]:
    """Return the first matching intent key, or None."""
    for intent, pattern in _PATTERNS.items():
        if pattern.search(message):
            return intent
    return None


def fetch_book_stats() -> Dict:
    """Fetch summary stats from book-service (total, price range, stock)."""
    url = f"{settings.BOOK_SERVICE_URL}/api/books/"
    try:
        # Get total count + most expensive
        resp = requests.get(url, params={"page_size": 1, "ordering": "-price"}, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        total = data.get("count", 0)
        top_price = data["results"][0] if data.get("results") else None

        # Get cheapest
        resp2 = requests.get(url, params={"page_size": 1, "ordering": "price"}, timeout=5)
        resp2.raise_for_status()
        cheapest = resp2.json().get("results", [None])[0]

        # Get in-stock count
        resp3 = requests.get(url, params={"page_size": 1, "in_stock": "true"}, timeout=5)
        resp3.raise_for_status()
        in_stock = resp3.json().get("count", 0)

        return {
            "total": total,
            "in_stock": in_stock,
            "out_of_stock": total - in_stock,
            "most_expensive": _format_book_short(top_price) if top_price else None,
            "cheapest": _format_book_short(cheapest) if cheapest else None,
        }
    except Exception as e:
        logger.warning(f"Failed to fetch book stats: {e}")
        return {}


def fetch_for_intent(intent: str) -> str:
    """Fetch data from book-service based on detected intent, return as text context."""
    url = f"{settings.BOOK_SERVICE_URL}/api/books/"
    try:
        if intent == "most_expensive":
            data = _fetch(url, {"ordering": "-price", "page_size": 5})
            return _format_list("Top 5 sách đắt nhất", data)

        if intent == "cheapest":
            data = _fetch(url, {"ordering": "price", "page_size": 5})
            return _format_list("Top 5 sách rẻ nhất", data)

        if intent == "newest":
            data = _fetch(url, {"ordering": "-created_at", "page_size": 5})
            return _format_list("Top 5 sách mới nhất", data)

        if intent == "count":
            resp = requests.get(url, params={"page_size": 1}, timeout=5)
            resp.raise_for_status()
            total = resp.json().get("count", 0)
            resp2 = requests.get(url, params={"page_size": 1, "in_stock": "true"}, timeout=5)
            resp2.raise_for_status()
            in_stock = resp2.json().get("count", 0)
            return (
                f"Thống kê kho sách:\n"
                f"- Tổng số sách: {total} cuốn\n"
                f"- Còn hàng: {in_stock} cuốn\n"
                f"- Hết hàng: {total - in_stock} cuốn"
            )

        if intent == "in_stock":
            resp = requests.get(url, params={"page_size": 1, "in_stock": "true"}, timeout=5)
            resp.raise_for_status()
            count = resp.json().get("count", 0)
            return f"Hiện có {count} cuốn sách còn hàng."

        if intent == "out_of_stock":
            total_resp = requests.get(url, params={"page_size": 1}, timeout=5)
            total_resp.raise_for_status()
            total = total_resp.json().get("count", 0)
            stock_resp = requests.get(url, params={"page_size": 1, "in_stock": "true"}, timeout=5)
            stock_resp.raise_for_status()
            in_stock = stock_resp.json().get("count", 0)
            return f"Hiện có {total - in_stock} cuốn sách hết hàng (trên tổng {total} cuốn)."

    except Exception as e:
        logger.warning(f"Smart query failed for intent '{intent}': {e}")

    return ""


def build_stats_summary() -> str:
    """Build a short stats summary to always include in context."""
    stats = fetch_book_stats()
    if not stats:
        return ""
    parts = [f"[Thông tin tổng quan cửa hàng]"]
    parts.append(f"Tổng số sách: {stats['total']} cuốn")
    parts.append(f"Còn hàng: {stats['in_stock']} cuốn")
    if stats.get("most_expensive"):
        parts.append(f"Sách đắt nhất: {stats['most_expensive']}")
    if stats.get("cheapest"):
        parts.append(f"Sách rẻ nhất: {stats['cheapest']}")
    return "\n".join(parts)


def enrich_with_related_books(search_results: list) -> str:
    """
    KB-lite: given RAG search results, find related books via book-service API.
    Looks up same author and same category for the top-scored book result.
    """
    # Find the best book hit from search results
    best_book = None
    for result in search_results:
        meta = result.get("metadata", {})
        if meta.get("source_type") == "book" and meta.get("book_id"):
            best_book = meta
            break

    if not best_book:
        return ""

    url = f"{settings.BOOK_SERVICE_URL}/api/books/"
    book_id = best_book.get("book_id")
    author = best_book.get("author", "")
    sections = []

    try:
        # Same author (exclude current book)
        if author:
            author_books = _fetch(url, {"author": author, "page_size": 5})
            author_books = [b for b in author_books if str(b.get("id")) != str(book_id)]
            if author_books:
                sections.append(_format_list(f"Sách cùng tác giả {author}", author_books[:3]))

        # Same category
        detail = _fetch_detail(book_id)
        if detail:
            cat_id = detail.get("category_id")
            if cat_id:
                cat_books = _fetch(url, {"category_id": cat_id, "page_size": 6})
                cat_books = [b for b in cat_books if str(b.get("id")) != str(book_id)]
                if cat_books:
                    sections.append(_format_list("Sách cùng thể loại", cat_books[:3]))
    except Exception as e:
        logger.warning(f"KB-lite enrichment failed: {e}")

    return "\n\n".join(sections)


def _fetch_detail(book_id: str) -> dict:
    """Fetch single book detail."""
    try:
        resp = requests.get(
            f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/", timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


# ---- helpers ----

def _fetch(url: str, params: dict) -> list:
    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", data) if isinstance(data, dict) else data


def _format_book_short(book: dict) -> str:
    title = book.get("title", "?")
    author = book.get("author", "")
    price = book.get("price", "?")
    stock = book.get("stock", 0)
    status_text = "còn hàng" if stock > 0 else "hết hàng"
    parts = [f'"{title}"']
    if author:
        parts.append(f"của {author}")
    parts.append(f"- {price} VND ({status_text})")
    return " ".join(parts)


def _format_list(heading: str, books: list) -> str:
    if not books:
        return ""
    lines = [f"{heading}:"]
    for i, book in enumerate(books, 1):
        lines.append(f"{i}. {_format_book_short(book)}")
    return "\n".join(lines)
