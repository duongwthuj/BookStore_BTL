"""
Views for chatbot service with RAG integration.
"""
import logging

from django.conf import settings as django_settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .services import book_service, order_service
from .openai_client import openai_client
from .gemini_client import gemini_client
from .ollama_client import ollama_client

logger = logging.getLogger(__name__)


def get_ai_response(message: str, context: str = None) -> dict:
    """Get AI response with fallback chain: OpenAI -> Gemini -> Ollama."""
    if django_settings.AI_PROVIDER == 'openai' and django_settings.OPENAI_API_KEY:
        result = openai_client.generate_response(message, context)
        if result['success']:
            return result

    if django_settings.GEMINI_API_KEY:
        result = gemini_client.generate_response(message, context)
        if result['success']:
            return result

    return ollama_client.generate_response(message, context)


ai_client = type('AIClient', (), {
    'generate_response': staticmethod(get_ai_response),
    'health_check': ollama_client.health_check,
})()


def _get_rag_modules():
    """Lazy import RAG modules to avoid startup errors if services aren't ready."""
    from .rag.rag_service import rag_service
    from .rag.mongo_store import mongo_store
    from .rag.document_processor import document_processor
    from .rag.vector_store import vector_store
    from .rag.embedding_service import embedding_service
    return rag_service, mongo_store, document_processor, vector_store, embedding_service


# ==================== CHAT ENDPOINTS ====================

@api_view(['POST'])
def chat(request):
    """
    RAG-enhanced chat endpoint.

    POST /chat/
    Body: {"message": "...", "session_id": "...(optional)"}
    Response: {"success": true, "response": "...", "sources": [...], "session_id": "..."}
    """
    message = request.data.get('message', '').strip()
    if not message:
        return Response(
            {"success": False, "error": "Message is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    session_id = request.data.get('session_id')

    try:
        rag_service, mongo_store, _, _, _ = _get_rag_modules()

        # Create session if needed
        if not session_id:
            user_id = request.headers.get('X-User-Id')
            session_id = mongo_store.create_session(user_id=user_id, title=message[:50])

        # Run RAG pipeline
        rag_result = rag_service.query(
            user_message=message,
            session_id=session_id,
        )

        # Generate response with RAG context
        result = ai_client.generate_response(message, rag_result.get("context_text"))

        if result['success']:
            # Save interaction
            rag_service.save_interaction(
                session_id=session_id,
                user_message=message,
                bot_response=result['response'],
                sources=rag_result.get('sources'),
            )

            return Response({
                "success": True,
                "response": result['response'],
                "model": result.get('model'),
                "sources": rag_result.get('sources', []),
                "session_id": session_id,
            })

        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    except Exception as e:
        logger.warning(f"RAG pipeline error, falling back to basic chat: {e}")
        # Fallback to basic chat without RAG
        context = request.data.get('context')
        result = ai_client.generate_response(message, context)
        if result['success']:
            response_data = {
                "success": True,
                "response": result['response'],
                "model": result.get('model'),
                "sources": [],
            }
            if session_id:
                response_data["session_id"] = session_id
            return Response(response_data)
        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def search_book(request):
    """
    Search for books via the chatbot.

    GET /chat/search-book/?q=Python
    """
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response(
            {"success": False, "error": "Query parameter 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = book_service.search_books(query)
    if not result['success']:
        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    books = result['books']

    if books:
        book_info = "\n".join([
            f"- {book.get('title', 'N/A')} - {book.get('author', 'N/A')} - {book.get('price', 'N/A')} VND"
            for book in books[:5]
        ])
        context = f"Kết quả tìm kiếm sách '{query}':\n{book_info}"
        prompt = f"Hãy giới thiệu ngắn gọn các sách tìm được với từ khóa '{query}'"
    else:
        context = f"Không tìm thấy sách nào với từ khóa '{query}'"
        prompt = f"Thông báo không tìm thấy sách với từ khóa '{query}' và gợi ý người dùng thử từ khóa khác"

    ollama_result = ai_client.generate_response(prompt, context)

    return Response({
        "success": True,
        "books": books,
        "count": len(books),
        "message": ollama_result.get('response', '') if ollama_result['success'] else None,
    })


@api_view(['GET'])
def order_status(request, order_id):
    """
    Check order status via the chatbot.

    GET /chat/order-status/{order_id}/
    """
    if not order_id:
        return Response(
            {"success": False, "error": "Order ID is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = order_service.get_order_status(order_id)

    if not result['success']:
        if result['error'] == "Order not found":
            ollama_result = ai_client.generate_response(
                f"Thông báo không tìm thấy đơn hàng với mã {order_id}",
                "Đơn hàng không tồn tại trong hệ thống",
            )
            return Response({
                "success": False,
                "error": "Order not found",
                "message": ollama_result.get('response', '') if ollama_result['success'] else None,
            }, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    order = result['order']
    order_info = (
        f"Mã đơn hàng: {order.get('id', order_id)}\n"
        f"Trạng thái: {order.get('status', 'N/A')}\n"
        f"Tổng tiền: {order.get('total', 'N/A')} VND\n"
        f"Ngày đặt: {order.get('created_at', 'N/A')}"
    )

    ollama_result = ai_client.generate_response(
        f"Thông báo trạng thái đơn hàng {order_id}",
        order_info,
    )

    return Response({
        "success": True,
        "order": order,
        "message": ollama_result.get('response', '') if ollama_result['success'] else None,
    })


# ==================== SESSION ENDPOINTS ====================

@api_view(['GET', 'POST'])
def sessions(request):
    """
    GET /chat/sessions/ - List chat sessions
    POST /chat/sessions/ - Create new session
    """
    _, mongo_store, _, _, _ = _get_rag_modules()

    if request.method == 'GET':
        user_id = request.headers.get('X-User-Id')
        session_list = mongo_store.list_sessions(user_id=user_id)
        return Response({"success": True, "sessions": session_list})

    # POST
    user_id = request.headers.get('X-User-Id')
    title = request.data.get('title', 'Cuộc trò chuyện mới')
    session_id = mongo_store.create_session(user_id=user_id, title=title)
    return Response(
        {"success": True, "session_id": session_id},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'DELETE'])
def session_detail(request, session_id):
    """
    GET /chat/sessions/{session_id}/ - Get session with messages
    DELETE /chat/sessions/{session_id}/ - Delete session
    """
    _, mongo_store, _, _, _ = _get_rag_modules()

    if request.method == 'DELETE':
        mongo_store.delete_session(session_id)
        return Response({"success": True})

    # GET
    session = mongo_store.get_session(session_id)
    if not session:
        return Response(
            {"success": False, "error": "Session not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    messages = mongo_store.get_session_messages(session_id)
    return Response({
        "success": True,
        "session": session,
        "messages": messages,
    })


@api_view(['GET'])
def session_history(request, session_id):
    """
    GET /chat/history/{session_id}/ - Get session message history
    """
    _, mongo_store, _, _, _ = _get_rag_modules()

    messages = mongo_store.get_session_messages(session_id)
    return Response({"success": True, "messages": messages})


# ==================== DOCUMENT MANAGEMENT ====================

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def documents(request):
    """
    GET /chat/documents/ - List knowledge base documents
    POST /chat/documents/ - Upload document to knowledge base
    """
    _, mongo_store, document_processor, _, _ = _get_rag_modules()

    if request.method == 'GET':
        source_type = request.query_params.get('type')
        docs = mongo_store.list_documents(source_type=source_type)
        return Response({"success": True, "documents": docs})

    # POST - Upload document
    if 'file' in request.FILES:
        uploaded_file = request.FILES['file']
        title = request.data.get('title', uploaded_file.name)
        result = document_processor.process_uploaded_file(uploaded_file, title)
    elif 'text' in request.data:
        text = request.data['text']
        title = request.data.get('title', 'Untitled')
        source_type = request.data.get('source_type', 'manual')
        result = document_processor.process_text(text, title, source_type)
    else:
        return Response(
            {"success": False, "error": "Either 'file' or 'text' is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def document_detail(request, doc_id):
    """
    DELETE /chat/documents/{doc_id}/ - Delete a document
    """
    _, mongo_store, _, vector_store, _ = _get_rag_modules()

    doc = mongo_store.delete_document(doc_id)
    if not doc:
        return Response(
            {"success": False, "error": "Document not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Delete vectors
    vector_ids = doc.get("vector_ids", [])
    if vector_ids:
        try:
            vector_store.client.delete(
                collection_name=vector_store.collection_name,
                points_selector=vector_ids,
            )
        except Exception as e:
            logger.warning(f"Failed to delete vectors: {e}")

    return Response({"success": True})


# ==================== SYNC & ADMIN ====================

@api_view(['POST'])
def sync_books(request):
    """
    POST /chat/sync-books/ - Sync books from book-service to vector store
    """
    _, _, document_processor, _, _ = _get_rag_modules()
    result = document_processor.sync_books_from_service()

    if result['success']:
        return Response(result)
    return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def rag_stats(request):
    """
    GET /chat/rag-stats/ - Get RAG system statistics
    """
    _, mongo_store, _, vector_store, embedding_service = _get_rag_modules()

    stats = {
        "vector_store": vector_store.get_collection_info(),
        "documents": len(mongo_store.list_documents(limit=1000)),
        "embedding_model": embedding_service.model_name,
    }
    return Response({"success": True, "stats": stats})


# ==================== HEALTH ====================

@api_view(['GET'])
def health(request):
    """
    Health check endpoint.

    GET /chat/health/
    """
    ollama_healthy = ai_client.health_check()

    # Check RAG components
    rag_status = {}
    try:
        _, mongo_store, _, vector_store, embedding_service = _get_rag_modules()
        rag_status["qdrant"] = "connected" if vector_store.health_check() else "disconnected"
        rag_status["mongodb"] = "connected" if mongo_store.health_check() else "disconnected"
        rag_status["embedding"] = "loaded" if embedding_service._model is not None else "not_loaded"
    except Exception as e:
        rag_status["error"] = str(e)

    all_healthy = ollama_healthy and rag_status.get("qdrant") == "connected"

    return Response({
        "status": "healthy" if all_healthy else "degraded",
        "ollama": "connected" if ollama_healthy else "disconnected",
        "rag": rag_status,
    }, status=status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)
