"""
Document processor for ingesting files and text into the RAG pipeline.
"""
import logging
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings

from .chunking import text_chunker
from .embedding_service import embedding_service
from .vector_store import vector_store
from .mongo_store import mongo_store

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and ingest documents into the knowledge base."""

    def process_text(
        self,
        text: str,
        title: str,
        source_type: str = "manual",
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """Process raw text and add to knowledge base."""
        metadata = metadata or {}

        # Save document metadata to MongoDB
        doc_id = mongo_store.save_document({
            "title": title,
            "content": text[:1000],  # Store preview
            "source_type": source_type,
            "metadata": metadata,
            "chunk_count": 0,
            "created_at": datetime.utcnow().isoformat(),
        })

        # Chunk the text
        chunk_metadata = {
            "source_id": doc_id,
            "source_title": title,
            "source_type": source_type,
            **metadata,
        }
        chunks = text_chunker.chunk_text(text, chunk_metadata)

        if not chunks:
            return {"success": False, "error": "No valid chunks generated"}

        # Generate embeddings
        texts = [c["content"] for c in chunks]
        embeddings = embedding_service.embed_batch(texts)

        # Store in vector DB
        metadatas = [c["metadata"] for c in chunks]
        point_ids = vector_store.upsert_documents(texts, embeddings, metadatas)

        # Update document with chunk info
        mongo_store.update_document(doc_id, {
            "chunk_count": len(chunks),
            "vector_ids": point_ids,
        })

        logger.info(f"Processed document '{title}': {len(chunks)} chunks")
        return {
            "success": True,
            "document_id": doc_id,
            "chunks": len(chunks),
            "title": title,
        }

    def process_file(self, file_path: str, title: str = None) -> Dict:
        """Process a file (PDF, DOCX, TXT, MD) and add to knowledge base."""
        if not title:
            title = os.path.basename(file_path)

        ext = os.path.splitext(file_path)[1].lower()

        try:
            text = self._extract_text(file_path, ext)
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return {"success": False, "error": f"Failed to extract text: {str(e)}"}

        if not text or len(text.strip()) < 50:
            return {"success": False, "error": "Extracted text too short or empty"}

        return self.process_text(
            text=text,
            title=title,
            source_type=ext.lstrip('.') or "unknown",
            metadata={"file_name": os.path.basename(file_path)},
        )

    def process_uploaded_file(self, uploaded_file, title: str = None) -> Dict:
        """Process a Django UploadedFile."""
        if not title:
            title = uploaded_file.name

        ext = os.path.splitext(uploaded_file.name)[1].lower()

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            result = self.process_file(tmp_path, title)
        finally:
            os.unlink(tmp_path)

        return result

    def sync_books_from_service(self) -> Dict:
        """Fetch all books from book-service and index them."""
        import requests

        books = []
        url = f"{settings.BOOK_SERVICE_URL}/api/books/"
        params = {"page_size": 200}

        try:
            while url:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, dict) and "results" in data:
                    books.extend(data["results"])
                    url = data.get("next")
                    params = {}  # next URL already has params
                elif isinstance(data, list):
                    books.extend(data)
                    url = None
                else:
                    url = None
        except Exception as e:
            logger.error(f"Failed to fetch books: {e}")
            return {"success": False, "error": str(e)}

        if not books:
            return {"success": True, "synced": 0, "message": "No books found"}

        # Delete existing book vectors
        try:
            vector_store.delete_by_source("book_catalog")
        except Exception:
            pass

        # Build text for each book
        texts = []
        metadatas = []
        for book in books:
            book_text = self._build_book_text(book)
            if len(book_text.strip()) < 20:
                continue
            texts.append(book_text)
            metadatas.append({
                "source_id": "book_catalog",
                "source_type": "book",
                "source_title": book.get("title", "Unknown"),
                "book_id": str(book.get("id", "")),
                "author": book.get("author", ""),
                "price": str(book.get("price", "")),
                "category": book.get("category_name", book.get("category", "")),
            })

        # Generate embeddings
        embeddings = embedding_service.embed_batch(texts)

        # Store in vector DB
        point_ids = vector_store.upsert_documents(texts, embeddings, metadatas)

        # Save sync record
        mongo_store.save_document({
            "title": "Book Catalog Sync",
            "source_type": "book_sync",
            "book_count": len(texts),
            "created_at": datetime.utcnow().isoformat(),
        })

        logger.info(f"Synced {len(texts)} books to vector store")
        return {
            "success": True,
            "synced": len(texts),
            "message": f"Successfully synced {len(texts)} books",
        }

    def upsert_single_book(self, book: Dict) -> Dict:
        """Add or update a single book in the vector store."""
        book_id = str(book.get("id", ""))
        if not book_id:
            return {"success": False, "error": "Book ID is required"}

        book_text = self._build_book_text(book)
        if len(book_text.strip()) < 20:
            return {"success": False, "error": "Book text too short"}

        # Delete existing vectors for this book
        try:
            vector_store.delete_by_book_id(book_id)
        except Exception:
            pass

        metadata = {
            "source_id": "book_catalog",
            "source_type": "book",
            "source_title": book.get("title", "Unknown"),
            "book_id": book_id,
            "author": book.get("author", ""),
            "price": str(book.get("price", "")),
            "category": book.get("category_name", book.get("category", "")),
        }

        embedding = embedding_service.embed_text(book_text)
        point_ids = vector_store.upsert_documents(
            [book_text], [embedding], [metadata]
        )

        logger.info(f"Upserted book '{book.get('title')}' (ID: {book_id})")
        return {"success": True, "book_id": book_id, "point_ids": point_ids}

    def delete_single_book(self, book_id: str) -> Dict:
        """Remove a single book from the vector store."""
        try:
            vector_store.delete_by_book_id(book_id)
            logger.info(f"Deleted book vectors for ID: {book_id}")
            return {"success": True, "book_id": book_id}
        except Exception as e:
            logger.error(f"Failed to delete book {book_id}: {e}")
            return {"success": False, "error": str(e)}

    def _build_book_text(self, book: Dict) -> str:
        """Build searchable text representation of a book."""
        parts = []
        if book.get("title"):
            parts.append(f"Tên sách: {book['title']}")
        if book.get("author"):
            parts.append(f"Tác giả: {book['author']}")
        if book.get("description"):
            parts.append(f"Mô tả: {book['description']}")
        if book.get("price"):
            parts.append(f"Giá: {book['price']} VND")
        if book.get("category_name") or book.get("category"):
            cat = book.get("category_name", book.get("category", ""))
            parts.append(f"Thể loại: {cat}")
        if book.get("publisher"):
            parts.append(f"Nhà xuất bản: {book['publisher']}")
        if book.get("isbn"):
            parts.append(f"ISBN: {book['isbn']}")
        if book.get("stock") is not None:
            status = "Còn hàng" if book['stock'] > 0 else "Hết hàng"
            parts.append(f"Tình trạng: {status}")
        return "\n".join(parts)

    def _extract_text(self, file_path: str, ext: str) -> str:
        """Extract text from a file."""
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(file_path)
            return result.text_content
        except ImportError:
            # Fallback: read as plain text
            if ext in ('.txt', '.md', '.csv'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            raise ValueError(f"Cannot process {ext} files without markitdown library")


document_processor = DocumentProcessor()
