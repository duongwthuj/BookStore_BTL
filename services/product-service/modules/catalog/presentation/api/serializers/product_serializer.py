from rest_framework import serializers
from modules.catalog.infrastructure.models.product_model import ProductModel


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = [
            'id', 'title', 'author', 'description', 'price', 'stock',
            'category_id', 'collection_ids', 'attributes', 'cover_image',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['id', 'title', 'author', 'price', 'stock', 'category_id', 'cover_image', 'created_at']


class StockUpdateSerializer(serializers.Serializer):
    stock = serializers.IntegerField(min_value=0)
