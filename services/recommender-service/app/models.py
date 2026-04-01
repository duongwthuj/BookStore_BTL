from django.db import models


class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('rate', 'Rate'),
    ]
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['book_id']),
        ]

    def __str__(self):
        return f"User {self.customer_id} - {self.interaction_type} - Book {self.book_id}"


class BookSimilarity(models.Model):
    book_id = models.IntegerField()
    similar_book_id = models.IntegerField()
    score = models.FloatField()  # Similarity score 0-1

    class Meta:
        unique_together = ['book_id', 'similar_book_id']
        indexes = [
            models.Index(fields=['book_id', '-score']),
        ]

    def __str__(self):
        return f"Book {self.book_id} ~ Book {self.similar_book_id} (score: {self.score})"
