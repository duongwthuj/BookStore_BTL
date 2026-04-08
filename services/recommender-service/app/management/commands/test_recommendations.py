"""
Test the recommender system APIs.
Usage: python manage.py test_recommendations
"""

from django.core.management.base import BaseCommand
from app.recommender import recommender_engine
from app.models import UserInteraction, BookSimilarity


class Command(BaseCommand):
    help = 'Test recommender system outputs'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('RECOMMENDER SYSTEM TEST')
        self.stdout.write('=' * 60)

        # Stats
        interactions = UserInteraction.objects.count()
        similarities = BookSimilarity.objects.count()
        self.stdout.write(f'\nData stats:')
        self.stdout.write(f'  - Total interactions: {interactions}')
        self.stdout.write(f'  - Total similarities: {similarities}')

        if interactions == 0:
            self.stdout.write(self.style.ERROR('\nNo data! Run seed_interactions first.'))
            return

        # Test 1: Popular books
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('TEST 1: Popular Books (last 30 days)')
        self.stdout.write('-' * 60)
        popular = recommender_engine.get_popular_books(limit=5)
        if popular:
            for i, rec in enumerate(popular, 1):
                self.stdout.write(
                    f'  {i}. Book {rec["book_id"]} - score: {rec["score"]:.2f} ({rec["reason"]})'
                )
        else:
            self.stdout.write('  No popular books found')

        # Test 2: Trending books
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('TEST 2: Trending Books (last 7 days)')
        self.stdout.write('-' * 60)
        trending = recommender_engine.get_trending_books(limit=5)
        if trending:
            for i, rec in enumerate(trending, 1):
                self.stdout.write(
                    f'  {i}. Book {rec["book_id"]} - score: {rec["score"]:.2f} ({rec["reason"]})'
                )
        else:
            self.stdout.write('  No trending books found')

        # Test 3: Similar books
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('TEST 3: Similar Books (for book_id=1)')
        self.stdout.write('-' * 60)
        # Get a book that has interactions
        sample_book = UserInteraction.objects.values('book_id').first()
        if sample_book:
            book_id = sample_book['book_id']
            similar = recommender_engine.get_similar_books(book_id, limit=5)
            self.stdout.write(f'  Similar to Book {book_id}:')
            if similar:
                for i, rec in enumerate(similar, 1):
                    self.stdout.write(
                        f'    {i}. Book {rec["book_id"]} - score: {rec["score"]:.2f} ({rec["reason"]})'
                    )
            else:
                self.stdout.write('    No similar books found')

        # Test 4: Personalized recommendations
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('TEST 4: Personalized Recommendations')
        self.stdout.write('-' * 60)
        # Get a user with interactions
        sample_user = UserInteraction.objects.values('customer_id').first()
        if sample_user:
            customer_id = sample_user['customer_id']

            # Show user's history
            user_history = UserInteraction.objects.filter(
                customer_id=customer_id
            ).values_list('book_id', 'interaction_type')[:5]
            self.stdout.write(f'  User {customer_id} history:')
            for book_id, itype in user_history:
                self.stdout.write(f'    - Book {book_id} ({itype})')

            # Get recommendations
            personalized = recommender_engine.get_personalized_recommendations(
                customer_id, limit=5
            )
            self.stdout.write(f'\n  Recommendations for User {customer_id}:')
            if personalized:
                for i, rec in enumerate(personalized, 1):
                    self.stdout.write(
                        f'    {i}. Book {rec["book_id"]} - score: {rec["score"]:.2f} ({rec["reason"]})'
                    )
            else:
                self.stdout.write('    No personalized recommendations found')

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('TEST COMPLETED'))
        self.stdout.write('=' * 60)
