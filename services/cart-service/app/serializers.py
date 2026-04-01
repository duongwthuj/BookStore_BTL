from rest_framework import serializers
from .models import Cart, CartItem
from .services import book_service, BookServiceError


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    book = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'book_id', 'book', 'quantity', 'price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'price', 'created_at', 'updated_at']

    def get_book(self, obj):
        """Get book details from book service."""
        try:
            book_data = book_service.get_book(obj.book_id)
            return {
                'id': book_data.get('id'),
                'title': book_data.get('title'),
                'author': book_data.get('author'),
                'price': book_data.get('price'),
                'image': book_data.get('cover_image') or book_data.get('image'),
                'stock': book_data.get('stock', 0),
            }
        except BookServiceError:
            return {
                'id': obj.book_id,
                'title': 'Unknown Book',
                'author': '',
                'price': float(obj.price),
                'image': None,
                'stock': 0,
            }


class CartItemCreateSerializer(serializers.Serializer):
    """Serializer for creating a cart item."""
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)


class CartItemUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    quantity = serializers.IntegerField(min_value=1)


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model with items."""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'items', 'total', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total(self, obj):
        """Calculate total price of all items in the cart."""
        return sum(item.price * item.quantity for item in obj.items.all())

    def get_item_count(self, obj):
        """Get total number of items in the cart."""
        return sum(item.quantity for item in obj.items.all())


class CartCreateSerializer(serializers.Serializer):
    """Serializer for creating a cart."""
    customer_id = serializers.IntegerField()
