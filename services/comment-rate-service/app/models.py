from django.db import models


class Review(models.Model):
    book_id = models.IntegerField()
    customer_id = models.IntegerField(null=True, blank=True)  # Null = guest
    customer_name = models.CharField(max_length=255, blank=True)  # For display
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    images = models.JSONField(default=list)  # List of image URLs
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['book_id']),
            models.Index(fields=['customer_id']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"Review {self.id} for Book {self.book_id} by {self.customer_name or 'Guest'}"


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    staff_id = models.IntegerField()
    staff_name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.staff_name} to Review {self.review_id}"
