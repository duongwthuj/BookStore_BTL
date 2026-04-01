from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category_id = models.IntegerField()  # FK to catalog-service
    collection_ids = models.JSONField(default=list)  # List of collection IDs
    cover_image = models.URLField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category_id']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['isbn']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"
