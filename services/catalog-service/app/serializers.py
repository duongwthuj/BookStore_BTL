from rest_framework import serializers
from .models import Category, Collection


class RecursiveCategorySerializer(serializers.Serializer):
    """Serializer for nested category structure."""
    def to_representation(self, instance):
        serializer = CategorySerializer(instance, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveCategorySerializer(many=True, read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='parent',
        allow_null=True,
        required=False
    )

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'parent_id',
            'children',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer for listing categories with nested structure."""
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'parent',
            'children',
            'created_at',
            'updated_at'
        ]

    def get_children(self, obj):
        children = obj.children.all()
        return CategoryListSerializer(children, many=True).data


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
