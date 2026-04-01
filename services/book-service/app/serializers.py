from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'description',
            'price',
            'stock',
            'category_id',
            'collection_ids',
            'cover_image',
            'isbn',
            'publisher',
            'published_date',
            'pages',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'price',
            'stock',
            'category_id',
            'cover_image',
            'created_at',
        ]


class StockUpdateSerializer(serializers.Serializer):
    stock = serializers.IntegerField(min_value=0)
