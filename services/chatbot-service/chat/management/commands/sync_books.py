"""
Management command to sync books from book-service into Qdrant vector store.

Usage:
    python manage.py sync_books
    python manage.py sync_books --force
"""
from django.core.management.base import BaseCommand

from chat.rag.document_processor import document_processor
from chat.rag.vector_store import vector_store


class Command(BaseCommand):
    help = 'Sync books from book-service into the RAG vector store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-sync even if vector store already has data',
        )

    def handle(self, *args, **options):
        force = options['force']

        if not force:
            try:
                info = vector_store.get_collection_info()
                count = info.get('points_count', 0)
                if count > 0:
                    self.stdout.write(
                        f"Vector store already has {count} points. "
                        "Use --force to re-sync."
                    )
                    return
            except Exception:
                pass

        self.stdout.write("Syncing books from book-service...")
        result = document_processor.sync_books_from_service()

        if result['success']:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully synced {result['synced']} books"
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"Sync failed: {result.get('error', 'Unknown error')}"
            ))
