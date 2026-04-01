from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import UserInteraction
from .serializers import (
    UserInteractionSerializer,
    RecommendationSerializer,
    ComputeSimilaritySerializer,
)
from .recommender import recommender_engine


@api_view(['GET'])
def similar_books(request, book_id):
    """
    GET /recommend/book/{book_id}/
    Get similar books for a given book (for book detail page).
    """
    limit = int(request.query_params.get('limit', 10))
    recommendations = recommender_engine.get_similar_books(book_id, limit=limit)
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response({
        'book_id': book_id,
        'recommendations': serializer.data
    })


@api_view(['GET'])
def personalized_recommendations(request, customer_id):
    """
    GET /recommend/user/{customer_id}/
    Get personalized recommendations for a user (for homepage).
    """
    limit = int(request.query_params.get('limit', 10))
    recommendations = recommender_engine.get_personalized_recommendations(customer_id, limit=limit)
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response({
        'customer_id': customer_id,
        'recommendations': serializer.data
    })


@api_view(['GET'])
def popular_books(request):
    """
    GET /recommend/popular/
    Get popular books (most purchased/viewed in last 30 days).
    """
    limit = int(request.query_params.get('limit', 10))
    recommendations = recommender_engine.get_popular_books(limit=limit)
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response({
        'recommendations': serializer.data
    })


@api_view(['GET'])
def trending_books(request):
    """
    GET /recommend/trending/
    Get trending books (recent interactions velocity).
    """
    limit = int(request.query_params.get('limit', 10))
    recommendations = recommender_engine.get_trending_books(limit=limit)
    serializer = RecommendationSerializer(recommendations, many=True)
    return Response({
        'recommendations': serializer.data
    })


@api_view(['POST'])
def record_interaction(request):
    """
    POST /interactions/
    Record a user interaction with a book.

    Request body:
    {
        "customer_id": 1,
        "book_id": 123,
        "interaction_type": "view|cart|purchase|rate",
        "rating": 5  // optional, required for "rate" type
    }
    """
    serializer = UserInteractionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def compute_similarity(request):
    """
    POST /similarity/compute/
    Compute book similarities (background job trigger).

    Request body (optional):
    {
        "book_ids": [1, 2, 3]  // If empty, computes for all books
    }
    """
    serializer = ComputeSimilaritySerializer(data=request.data)
    if serializer.is_valid():
        book_ids = serializer.validated_data.get('book_ids')
        result = recommender_engine.compute_similarities(book_ids)
        return Response({
            'status': 'completed',
            'result': result
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def health_check(request):
    """
    GET /health/
    Health check endpoint.
    """
    return Response({'status': 'healthy', 'service': 'recommender-service'})
