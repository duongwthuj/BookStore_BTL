from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Review, ReviewReply
from .serializers import (
    RatingStatsSerializer,
    ReviewCreateSerializer,
    ReviewReplyCreateSerializer,
    ReviewSerializer,
)
from .services import order_service


class BookReviewListView(ListAPIView):
    """GET /reviews/book/{book_id}/ - Reviews for a book (with pagination)"""
    serializer_class = ReviewSerializer

    def get_queryset(self):
        book_id = self.kwargs['book_id']
        return Review.objects.filter(book_id=book_id).prefetch_related('replies')


class ReviewCreateView(CreateAPIView):
    """POST /reviews/ - Create review"""
    serializer_class = ReviewCreateSerializer

    def perform_create(self, serializer):
        customer_id = serializer.validated_data.get('customer_id')
        book_id = serializer.validated_data.get('book_id')

        # Verify purchase if customer_id is provided
        is_verified = False
        if customer_id:
            is_verified = order_service.verify_purchase(customer_id, book_id)

        serializer.save(is_verified_purchase=is_verified)


class BookRatingStatsView(APIView):
    """GET /reviews/book/{book_id}/stats/ - Rating statistics"""

    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id)

        # Calculate average rating
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )

        average_rating = stats['average_rating'] or 0
        total_reviews = stats['total_reviews']

        # Calculate rating distribution
        distribution = reviews.values('rating').annotate(count=Count('id'))
        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for item in distribution:
            rating_distribution[str(item['rating'])] = item['count']

        data = {
            'average_rating': round(average_rating, 2),
            'total_reviews': total_reviews,
            'rating_distribution': rating_distribution,
        }

        serializer = RatingStatsSerializer(data)
        return Response(serializer.data)


class ReviewDetailView(RetrieveAPIView):
    """GET /reviews/{id}/ - Review detail"""
    queryset = Review.objects.prefetch_related('replies')
    serializer_class = ReviewSerializer


class ReviewDeleteView(DestroyAPIView):
    """DELETE /reviews/{id}/ - Delete review (Staff)"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewReplyCreateView(CreateAPIView):
    """POST /reviews/{id}/reply/ - Staff reply to review"""
    serializer_class = ReviewReplyCreateSerializer

    def perform_create(self, serializer):
        review_id = self.kwargs['pk']
        review = Review.objects.get(pk=review_id)
        serializer.save(review=review)

    def create(self, request, *args, **kwargs):
        try:
            review_id = self.kwargs['pk']
            Review.objects.get(pk=review_id)
        except Review.DoesNotExist:
            return Response(
                {'error': 'Review not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().create(request, *args, **kwargs)


class CustomerReviewListView(ListAPIView):
    """GET /reviews/customer/{customer_id}/ - Reviews by customer"""
    serializer_class = ReviewSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Review.objects.filter(customer_id=customer_id).prefetch_related('replies')
