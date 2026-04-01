"""
Views for chatbot service.
"""
from django.conf import settings as django_settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import book_service, order_service
from .openai_client import openai_client
from .gemini_client import gemini_client
from .ollama_client import ollama_client


def get_ai_response(message: str, context: str = None) -> dict:
    """Get AI response with fallback chain: OpenAI -> Gemini -> Ollama."""
    # Try OpenAI first if configured
    if django_settings.AI_PROVIDER == 'openai' and django_settings.OPENAI_API_KEY:
        result = openai_client.generate_response(message, context)
        if result['success']:
            return result

    # Try Gemini if configured
    if django_settings.GEMINI_API_KEY:
        result = gemini_client.generate_response(message, context)
        if result['success']:
            return result

    # Fallback to Ollama
    return ollama_client.generate_response(message, context)


# Alias for backwards compatibility
ai_client = type('AIClient', (), {'generate_response': staticmethod(get_ai_response), 'health_check': ollama_client.health_check})()


@api_view(['POST'])
def chat(request):
    """
    Send a message to the chatbot and receive a response.

    POST /chat/
    Body: {"message": "Xin chào"}

    Response: {"success": true, "response": "...", "model": "llama3.2:1b"}
    """
    message = request.data.get('message', '').strip()

    if not message:
        return Response(
            {"success": False, "error": "Message is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get optional context
    context = request.data.get('context')

    # Generate response from Ollama
    result = ai_client.generate_response(message, context)

    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def search_book(request):
    """
    Search for books via the chatbot.

    GET /chat/search-book/?q=Python

    Response: {"success": true, "books": [...], "message": "..."}
    """
    query = request.query_params.get('q', '').strip()

    if not query:
        return Response(
            {"success": False, "error": "Query parameter 'q' is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Search books from book-service
    result = book_service.search_books(query)

    if not result['success']:
        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    books = result['books']

    # Generate a friendly response using Ollama
    if books:
        book_info = "\n".join([
            f"- {book.get('title', 'N/A')} - {book.get('author', 'N/A')} - {book.get('price', 'N/A')} VND"
            for book in books[:5]  # Limit to 5 books
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
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def order_status(request, order_id):
    """
    Check order status via the chatbot.

    GET /chat/order-status/{order_id}/

    Response: {"success": true, "order": {...}, "message": "..."}
    """
    if not order_id:
        return Response(
            {"success": False, "error": "Order ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get order from order-service
    result = order_service.get_order_status(order_id)

    if not result['success']:
        if result['error'] == "Order not found":
            # Generate friendly not found message
            ollama_result = ai_client.generate_response(
                f"Thông báo không tìm thấy đơn hàng với mã {order_id}",
                "Đơn hàng không tồn tại trong hệ thống"
            )
            return Response({
                "success": False,
                "error": "Order not found",
                "message": ollama_result.get('response', '') if ollama_result['success'] else None,
            }, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    order = result['order']

    # Generate a friendly response using Ollama
    order_info = f"""
    Mã đơn hàng: {order.get('id', order_id)}
    Trạng thái: {order.get('status', 'N/A')}
    Tổng tiền: {order.get('total', 'N/A')} VND
    Ngày đặt: {order.get('created_at', 'N/A')}
    """

    ollama_result = ai_client.generate_response(
        f"Thông báo trạng thái đơn hàng {order_id}",
        order_info
    )

    return Response({
        "success": True,
        "order": order,
        "message": ollama_result.get('response', '') if ollama_result['success'] else None,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def health(request):
    """
    Health check endpoint.

    GET /chat/health/
    """
    ollama_healthy = ai_client.health_check()

    return Response({
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama": "connected" if ollama_healthy else "disconnected",
    }, status=status.HTTP_200_OK if ollama_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)
