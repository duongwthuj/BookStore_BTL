"""
Recommendation algorithms for the hybrid recommender system.
"""

import logging
from collections import defaultdict
from datetime import timedelta
from typing import Optional

from django.db.models import Count, Sum, Case, When, IntegerField, F
from django.utils import timezone

from .models import UserInteraction, BookSimilarity
from .services import book_service

logger = logging.getLogger(__name__)

# Interaction weights for scoring
INTERACTION_WEIGHTS = {
    'purchase': 5.0,
    'cart': 3.0,
    'rate': 2.0,
    'view': 1.0,
}


class RecommenderEngine:
    """Hybrid recommendation engine combining multiple strategies."""

    def __init__(self):
        self.book_client = book_service

    def get_similar_books(self, book_id: int, limit: int = 10) -> list[dict]:
        """
        Get similar books for a given book (for book detail page).
        Uses hybrid approach: precomputed similarities + content-based fallback.
        """
        recommendations = []

        # 1. Get precomputed similarities (collaborative filtering based)
        similarities = BookSimilarity.objects.filter(
            book_id=book_id
        ).order_by('-score')[:limit]

        similar_book_ids = [s.similar_book_id for s in similarities]
        similarity_scores = {s.similar_book_id: s.score for s in similarities}

        for sim_book_id in similar_book_ids:
            recommendations.append({
                'book_id': sim_book_id,
                'score': similarity_scores[sim_book_id],
                'reason': 'collaborative'
            })

        # 2. Content-based fallback if not enough recommendations
        if len(recommendations) < limit:
            content_recs = self._get_content_based_recommendations(book_id, limit - len(recommendations))
            existing_ids = {r['book_id'] for r in recommendations}
            for rec in content_recs:
                if rec['book_id'] not in existing_ids and rec['book_id'] != book_id:
                    recommendations.append(rec)

        # Enrich with book details
        return self._enrich_with_book_details(recommendations[:limit])

    def get_personalized_recommendations(self, customer_id: int, limit: int = 10) -> list[dict]:
        """
        Get personalized recommendations for a user (for homepage).
        Uses hybrid approach: collaborative + content-based + popular fallback.
        """
        recommendations = []
        seen_book_ids = set()

        # Get user's interaction history
        user_interactions = UserInteraction.objects.filter(
            customer_id=customer_id
        ).values_list('book_id', flat=True).distinct()
        interacted_books = set(user_interactions)

        # 1. Collaborative: Books similar to what user interacted with
        collab_recs = self._get_collaborative_recommendations(customer_id, limit * 2)
        for rec in collab_recs:
            if rec['book_id'] not in interacted_books and rec['book_id'] not in seen_book_ids:
                recommendations.append(rec)
                seen_book_ids.add(rec['book_id'])
                if len(recommendations) >= limit:
                    break

        # 2. Content-based: Same categories/authors as user's favorites
        if len(recommendations) < limit:
            content_recs = self._get_user_content_recommendations(customer_id, limit)
            for rec in content_recs:
                if rec['book_id'] not in interacted_books and rec['book_id'] not in seen_book_ids:
                    recommendations.append(rec)
                    seen_book_ids.add(rec['book_id'])
                    if len(recommendations) >= limit:
                        break

        # 3. Popular fallback for new/inactive users
        if len(recommendations) < limit:
            popular_recs = self.get_popular_books(limit)
            for rec in popular_recs:
                if rec['book_id'] not in interacted_books and rec['book_id'] not in seen_book_ids:
                    rec['reason'] = 'popular_fallback'
                    recommendations.append(rec)
                    seen_book_ids.add(rec['book_id'])
                    if len(recommendations) >= limit:
                        break

        return self._enrich_with_book_details(recommendations[:limit])

    def get_popular_books(self, limit: int = 10) -> list[dict]:
        """
        Get popular books based on weighted interactions in last 30 days.
        """
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Calculate weighted popularity score
        popular_books = UserInteraction.objects.filter(
            created_at__gte=thirty_days_ago
        ).values('book_id').annotate(
            score=Sum(
                Case(
                    When(interaction_type='purchase', then=INTERACTION_WEIGHTS['purchase']),
                    When(interaction_type='cart', then=INTERACTION_WEIGHTS['cart']),
                    When(interaction_type='rate', then=INTERACTION_WEIGHTS['rate']),
                    When(interaction_type='view', then=INTERACTION_WEIGHTS['view']),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by('-score')[:limit]

        recommendations = [
            {
                'book_id': item['book_id'],
                'score': float(item['score']) / 10,  # Normalize score
                'reason': 'popular'
            }
            for item in popular_books
        ]

        return self._enrich_with_book_details(recommendations)

    def get_trending_books(self, limit: int = 10) -> list[dict]:
        """
        Get trending books based on recent interactions (last 7 days).
        Focuses on velocity of interactions rather than absolute numbers.
        """
        seven_days_ago = timezone.now() - timedelta(days=7)
        one_day_ago = timezone.now() - timedelta(days=1)

        # Recent interactions (last 24 hours) weighted higher
        trending_books = UserInteraction.objects.filter(
            created_at__gte=seven_days_ago
        ).values('book_id').annotate(
            recent_count=Count(
                Case(When(created_at__gte=one_day_ago, then=1))
            ),
            week_count=Count('id'),
            score=F('recent_count') * 3 + F('week_count')
        ).order_by('-score')[:limit]

        recommendations = [
            {
                'book_id': item['book_id'],
                'score': float(item['score']) / 10,  # Normalize
                'reason': 'trending'
            }
            for item in trending_books
        ]

        return self._enrich_with_book_details(recommendations)

    def compute_similarities(self, book_ids: Optional[list[int]] = None) -> dict:
        """
        Compute book similarities based on collaborative filtering.
        Uses co-occurrence: books bought/viewed together by same users.
        """
        # Get all interactions or filter by book_ids
        if book_ids:
            interactions = UserInteraction.objects.filter(book_id__in=book_ids)
        else:
            interactions = UserInteraction.objects.all()

        # Build user-book matrix
        user_books = defaultdict(set)
        for interaction in interactions.values('customer_id', 'book_id', 'interaction_type'):
            weight = INTERACTION_WEIGHTS.get(interaction['interaction_type'], 1)
            if weight >= 2:  # Only consider meaningful interactions
                user_books[interaction['customer_id']].add(interaction['book_id'])

        # Compute co-occurrence
        co_occurrence = defaultdict(lambda: defaultdict(int))
        book_counts = defaultdict(int)

        for user_id, books in user_books.items():
            books_list = list(books)
            for i, book1 in enumerate(books_list):
                book_counts[book1] += 1
                for book2 in books_list[i + 1:]:
                    co_occurrence[book1][book2] += 1
                    co_occurrence[book2][book1] += 1

        # Calculate similarity scores (Jaccard-like)
        similarities_created = 0
        similarities_updated = 0

        target_books = book_ids if book_ids else list(co_occurrence.keys())

        for book_id in target_books:
            similar_books = co_occurrence.get(book_id, {})
            for similar_book_id, co_count in similar_books.items():
                # Jaccard similarity: intersection / union
                union = book_counts[book_id] + book_counts[similar_book_id] - co_count
                score = co_count / union if union > 0 else 0

                if score > 0.05:  # Minimum threshold
                    obj, created = BookSimilarity.objects.update_or_create(
                        book_id=book_id,
                        similar_book_id=similar_book_id,
                        defaults={'score': round(score, 4)}
                    )
                    if created:
                        similarities_created += 1
                    else:
                        similarities_updated += 1

        return {
            'books_processed': len(target_books),
            'similarities_created': similarities_created,
            'similarities_updated': similarities_updated
        }

    def _get_collaborative_recommendations(self, customer_id: int, limit: int) -> list[dict]:
        """Get recommendations based on similar users' behavior."""
        # Get user's highly-weighted interactions
        user_books = UserInteraction.objects.filter(
            customer_id=customer_id,
            interaction_type__in=['purchase', 'cart', 'rate']
        ).values_list('book_id', flat=True).distinct()

        if not user_books:
            return []

        # Find similar books based on precomputed similarities
        similar_books = BookSimilarity.objects.filter(
            book_id__in=list(user_books)
        ).exclude(
            similar_book_id__in=list(user_books)
        ).values('similar_book_id').annotate(
            total_score=Sum('score')
        ).order_by('-total_score')[:limit]

        return [
            {
                'book_id': item['similar_book_id'],
                'score': float(item['total_score']),
                'reason': 'collaborative'
            }
            for item in similar_books
        ]

    def _get_content_based_recommendations(self, book_id: int, limit: int) -> list[dict]:
        """Get recommendations based on same category/author."""
        recommendations = []

        # Fetch the source book details
        book = self.book_client.get_book(book_id)
        if not book:
            return []

        # Get books from same category
        category_id = book.get('category') or book.get('category_id')
        if category_id:
            category_books = self.book_client.get_books_by_category(category_id, limit)
            for b in category_books:
                b_id = b.get('id')
                if b_id and b_id != book_id:
                    recommendations.append({
                        'book_id': b_id,
                        'score': 0.7,
                        'reason': 'same_category'
                    })

        # Get books from same author
        author_id = book.get('author') or book.get('author_id')
        if author_id and len(recommendations) < limit:
            author_books = self.book_client.get_books_by_author(author_id, limit)
            existing_ids = {r['book_id'] for r in recommendations}
            for b in author_books:
                b_id = b.get('id')
                if b_id and b_id != book_id and b_id not in existing_ids:
                    recommendations.append({
                        'book_id': b_id,
                        'score': 0.8,
                        'reason': 'same_author'
                    })

        return recommendations[:limit]

    def _get_user_content_recommendations(self, customer_id: int, limit: int) -> list[dict]:
        """Get content-based recommendations based on user's favorite categories/authors."""
        # Get user's most interacted books
        top_books = UserInteraction.objects.filter(
            customer_id=customer_id
        ).values('book_id').annotate(
            score=Sum(
                Case(
                    When(interaction_type='purchase', then=INTERACTION_WEIGHTS['purchase']),
                    When(interaction_type='cart', then=INTERACTION_WEIGHTS['cart']),
                    When(interaction_type='rate', then=INTERACTION_WEIGHTS['rate']),
                    default=1,
                    output_field=IntegerField()
                )
            )
        ).order_by('-score')[:5]

        recommendations = []
        seen_ids = set()

        for item in top_books:
            content_recs = self._get_content_based_recommendations(item['book_id'], limit // 2)
            for rec in content_recs:
                if rec['book_id'] not in seen_ids:
                    rec['reason'] = 'content_based'
                    recommendations.append(rec)
                    seen_ids.add(rec['book_id'])

        return recommendations[:limit]

    def _enrich_with_book_details(self, recommendations: list[dict]) -> list[dict]:
        """Add book metadata to recommendations."""
        if not recommendations:
            return recommendations

        book_ids = [r['book_id'] for r in recommendations]
        books = self.book_client.get_books(book_ids)

        for rec in recommendations:
            book_details = books.get(rec['book_id'])
            if book_details:
                rec['book_details'] = book_details

        return recommendations


# Singleton instance
recommender_engine = RecommenderEngine()
