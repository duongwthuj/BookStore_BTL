"""
Compute book similarities based on user interactions.
Usage: python manage.py compute_similarities
"""

from django.core.management.base import BaseCommand
from app.recommender import recommender_engine
from app.models import UserInteraction, BookSimilarity


class Command(BaseCommand):
    help = 'Compute book similarities for the recommender system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--book-ids', type=str, default='',
            help='Comma-separated book IDs to compute (default: all)'
        )

    def handle(self, *args, **options):
        # Check if we have interactions
        interaction_count = UserInteraction.objects.count()
        if interaction_count == 0:
            self.stdout.write(self.style.WARNING(
                'No interactions found! Run seed_interactions first.'
            ))
            return

        self.stdout.write(f'Found {interaction_count} interactions')

        # Parse book IDs if provided
        book_ids = None
        if options['book_ids']:
            book_ids = [int(x.strip()) for x in options['book_ids'].split(',')]
            self.stdout.write(f'Computing similarities for books: {book_ids}')
        else:
            self.stdout.write('Computing similarities for all books...')

        # Compute similarities
        result = recommender_engine.compute_similarities(book_ids)

        self.stdout.write(self.style.SUCCESS(f'\nResults:'))
        self.stdout.write(f'  - Books processed: {result["books_processed"]}')
        self.stdout.write(f'  - Similarities created: {result["similarities_created"]}')
        self.stdout.write(f'  - Similarities updated: {result["similarities_updated"]}')

        # Show sample similarities
        total_similarities = BookSimilarity.objects.count()
        self.stdout.write(f'\nTotal similarities in DB: {total_similarities}')

        if total_similarities > 0:
            self.stdout.write('\nSample similarities (top 10):')
            top_sims = BookSimilarity.objects.order_by('-score')[:10]
            for sim in top_sims:
                self.stdout.write(
                    f'  Book {sim.book_id} ~ Book {sim.similar_book_id}: {sim.score:.4f}'
                )

        self.stdout.write(self.style.SUCCESS('\nDone!'))
