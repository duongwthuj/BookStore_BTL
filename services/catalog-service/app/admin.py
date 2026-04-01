from django.contrib import admin
from .models import Category, Collection


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at', 'updated_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
