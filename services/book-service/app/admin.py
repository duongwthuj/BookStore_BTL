from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'price', 'stock', 'category_id', 'created_at']
    list_filter = ['category_id', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'publisher']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
