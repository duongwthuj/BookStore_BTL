from django.urls import path
from . import views

urlpatterns = [
    # Recommendation endpoints
    path('recommend/book/<int:book_id>/', views.similar_books, name='similar-books'),
    path('recommend/user/<int:customer_id>/', views.personalized_recommendations, name='personalized-recommendations'),
    path('recommend/popular/', views.popular_books, name='popular-books'),
    path('recommend/trending/', views.trending_books, name='trending-books'),

    # Interaction recording
    path('interactions/', views.record_interaction, name='record-interaction'),

    # Similarity computation (background job)
    path('similarity/compute/', views.compute_similarity, name='compute-similarity'),

    # Health check
    path('health/', views.health_check, name='health-check'),
]
