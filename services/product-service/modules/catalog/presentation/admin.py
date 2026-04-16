from django.contrib import admin
from modules.catalog.infrastructure.models.product_model import ProductModel


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'price', 'stock', 'category_id', 'created_at']
    list_filter = ['category_id', 'created_at']
    search_fields = ['title', 'author']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
