from django.db import models


class ProductModel(models.Model):
    """Django ORM model. Infrastructure concern only — domain uses Product entity."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category_id = models.IntegerField()
    collection_ids = models.JSONField(default=list)
    attributes = models.JSONField(default=dict)  # isbn, publisher, pages, published_date, etc.
    cover_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category_id']),
            models.Index(fields=['title']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"
