"""
Seed fake user interactions for testing the recommender system.
Usage: python manage.py seed_interactions
"""

import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import UserInteraction, BookSimilarity


class Command(BaseCommand):
    help = 'Seed fake user interactions for testing recommender system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users', type=int, default=100,
            help='Number of fake users (default: 100)'
        )
        parser.add_argument(
            '--books', type=int, default=50,
            help='Number of books (default: 50)'
        )
        parser.add_argument(
            '--interactions', type=int, default=1000,
            help='Number of interactions (default: 1000)'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_books = options['books']
        num_interactions = options['interactions']

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            UserInteraction.objects.all().delete()
            BookSimilarity.objects.all().delete()

        self.stdout.write(f'Seeding {num_interactions} interactions...')
        self.stdout.write(f'  - Users: 1 to {num_users}')
        self.stdout.write(f'  - Books: 1 to {num_books}')

        # Create user profiles (some users prefer certain categories)
        # Simulate: users 1-30 like books 1-20, users 31-60 like books 15-35, etc.
        user_preferences = {}
        for user_id in range(1, num_users + 1):
            # Each user has preferred book range (simulates category preference)
            start = random.randint(1, num_books - 10)
            end = min(start + random.randint(10, 20), num_books)
            user_preferences[user_id] = (start, end)

        interactions = []
        now = timezone.now()

        for _ in range(num_interactions):
            user_id = random.randint(1, num_users)
            pref_start, pref_end = user_preferences[user_id]

            # 70% chance to pick from preferred books, 30% random
            if random.random() < 0.7:
                book_id = random.randint(pref_start, pref_end)
            else:
                book_id = random.randint(1, num_books)

            # Interaction type distribution: view 60%, cart 20%, purchase 15%, rate 5%
            rand = random.random()
            if rand < 0.60:
                interaction_type = 'view'
            elif rand < 0.80:
                interaction_type = 'cart'
            elif rand < 0.95:
                interaction_type = 'purchase'
            else:
                interaction_type = 'rate'

            # Random timestamp in last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            created_at = now - timedelta(days=days_ago, hours=hours_ago)

            rating = None
            if interaction_type == 'rate':
                # Ratings tend to be positive (3-5 stars)
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]

            interactions.append(UserInteraction(
                customer_id=user_id,
                book_id=book_id,
                interaction_type=interaction_type,
                rating=rating,
                created_at=created_at,
            ))

        # Bulk create for performance
        UserInteraction.objects.bulk_create(interactions, batch_size=500)

        # Print stats
        stats = {
            'view': UserInteraction.objects.filter(interaction_type='view').count(),
            'cart': UserInteraction.objects.filter(interaction_type='cart').count(),
            'purchase': UserInteraction.objects.filter(interaction_type='purchase').count(),
            'rate': UserInteraction.objects.filter(interaction_type='rate').count(),
        }

        self.stdout.write(self.style.SUCCESS(f'\nCreated {num_interactions} interactions:'))
        for itype, count in stats.items():
            self.stdout.write(f'  - {itype}: {count}')

        self.stdout.write(self.style.SUCCESS('\nDone! Now run: python manage.py compute_similarities'))
