"""
MongoDB store for chat sessions, messages, and document metadata.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


def _to_object_id(id_str: str) -> Optional[ObjectId]:
    """Safely convert string to ObjectId."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        return None


class MongoStore:
    """MongoDB-backed storage for chat data and documents."""

    def __init__(self):
        self._client = None
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(settings.MONGODB_URL)
            self._db = self._client[settings.MONGODB_DB_NAME]
            self._ensure_indexes()
        return self._db

    def _ensure_indexes(self):
        """Create necessary indexes."""
        self._db.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)])
        self._db.chat_messages.create_index([("session_id", 1), ("created_at", 1)])
        self._db.documents.create_index([("source_type", 1)])

    # ==================== Chat Sessions ====================

    def create_session(self, user_id: str = None, title: str = "Cuộc trò chuyện mới") -> str:
        """Create a new chat session."""
        now = datetime.utcnow().isoformat()
        result = self.db.chat_sessions.insert_one({
            "user_id": user_id,
            "title": title,
            "message_count": 0,
            "created_at": now,
            "updated_at": now,
        })
        return str(result.inserted_id)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a session by ID."""
        oid = _to_object_id(session_id)
        if not oid:
            return None
        doc = self.db.chat_sessions.find_one({"_id": oid})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    def list_sessions(self, user_id: str = None, limit: int = 20) -> List[Dict]:
        """List recent chat sessions."""
        query = {}
        if user_id:
            query["user_id"] = user_id

        cursor = self.db.chat_sessions.find(query).sort(
            "updated_at", DESCENDING
        ).limit(limit)

        sessions = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            sessions.append(doc)
        return sessions

    def update_session_title(self, session_id: str, title: str):
        """Update session title."""
        oid = _to_object_id(session_id)
        if not oid:
            return
        self.db.chat_sessions.update_one(
            {"_id": oid},
            {"$set": {"title": title, "updated_at": datetime.utcnow().isoformat()}},
        )

    def delete_session(self, session_id: str):
        """Delete a session and its messages."""
        oid = _to_object_id(session_id)
        if not oid:
            return
        self.db.chat_sessions.delete_one({"_id": oid})
        self.db.chat_messages.delete_many({"session_id": session_id})

    # ==================== Chat Messages ====================

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: List[Dict] = None,
        metadata: Dict = None,
    ) -> str:
        """Save a chat message."""
        now = datetime.utcnow().isoformat()
        message = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "metadata": metadata or {},
            "created_at": now,
        }
        result = self.db.chat_messages.insert_one(message)

        # Update session
        oid = _to_object_id(session_id)
        if oid:
            self.db.chat_sessions.update_one(
                {"_id": oid},
                {
                    "$inc": {"message_count": 1},
                    "$set": {"updated_at": now},
                },
            )

        return str(result.inserted_id)

    def get_session_messages(
        self,
        session_id: str,
        limit: int = 50,
    ) -> List[Dict]:
        """Get messages for a session."""
        cursor = self.db.chat_messages.find(
            {"session_id": session_id}
        ).sort("created_at", 1).limit(limit)

        messages = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            messages.append(doc)
        return messages

    def get_recent_context(self, session_id: str, limit: int = 6) -> List[Dict]:
        """Get recent messages for conversation context."""
        cursor = self.db.chat_messages.find(
            {"session_id": session_id}
        ).sort("created_at", -1).limit(limit)

        messages = []
        for doc in cursor:
            messages.append({
                "role": doc["role"],
                "content": doc["content"],
            })
        messages.reverse()
        return messages

    # ==================== Documents ====================

    def save_document(self, doc: Dict) -> str:
        """Save document metadata."""
        result = self.db.documents.insert_one(doc)
        return str(result.inserted_id)

    def update_document(self, doc_id: str, update: Dict):
        """Update document metadata."""
        oid = _to_object_id(doc_id)
        if not oid:
            return
        self.db.documents.update_one(
            {"_id": oid},
            {"$set": update},
        )

    def list_documents(self, source_type: str = None, limit: int = 50) -> List[Dict]:
        """List documents."""
        query = {}
        if source_type:
            query["source_type"] = source_type

        cursor = self.db.documents.find(query).sort(
            "created_at", DESCENDING
        ).limit(limit)

        docs = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            docs.append(doc)
        return docs

    def delete_document(self, doc_id: str) -> Optional[Dict]:
        """Delete a document and return its data for cleanup."""
        oid = _to_object_id(doc_id)
        if not oid:
            return None
        doc = self.db.documents.find_one({"_id": oid})
        if doc:
            self.db.documents.delete_one({"_id": oid})
            doc["id"] = str(doc.pop("_id"))
            return doc
        return None

    def health_check(self) -> bool:
        try:
            self.db.command("ping")
            return True
        except Exception:
            return False


mongo_store = MongoStore()
