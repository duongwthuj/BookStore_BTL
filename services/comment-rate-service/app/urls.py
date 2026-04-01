from django.urls import path

from .views import (
    BookRatingStatsView,
    BookReviewListView,
    CustomerReviewListView,
    ReviewCreateView,
    ReviewDeleteView,
    ReviewDetailView,
    ReviewReplyCreateView,
)

urlpatterns = [
    # Reviews for a book
    path('reviews/book/<int:book_id>/', BookReviewListView.as_view(), name='book-reviews'),

    # Create review
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),

    # Rating statistics for a book
    path('reviews/book/<int:book_id>/stats/', BookRatingStatsView.as_view(), name='book-rating-stats'),

    # Review detail
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),

    # Delete review (Staff)
    path('reviews/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review-delete'),

    # Staff reply to review
    path('reviews/<int:pk>/reply/', ReviewReplyCreateView.as_view(), name='review-reply'),

    # Reviews by customer
    path('reviews/customer/<int:customer_id>/', CustomerReviewListView.as_view(), name='customer-reviews'),
]
