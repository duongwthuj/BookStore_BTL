from rest_framework import serializers
from .models import Order, OrderItem, Coupon


class OrderItemSerializer(serializers.ModelSerializer):
    item_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book_id', 'book_title', 'quantity', 'price', 'item_total']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_id', 'status', 'status_display',
            'shipping_address', 'phone', 'note', 'coupon_code',
            'payment_method', 'payment_method_display',
            'shipping_method', 'shipping_fee',
            'subtotal', 'discount', 'total',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an order from cart."""
    customer_id = serializers.IntegerField()
    shipping_address = serializers.CharField()
    phone = serializers.CharField(max_length=15)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    coupon_code = serializers.CharField(required=False, allow_blank=True, default='')
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)
    shipping_method = serializers.CharField(max_length=50)
    shipping_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="List of items: [{'book_id': 1, 'book_title': 'Title', 'quantity': 2, 'price': 10.00}]"
    )


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value',
            'min_order', 'max_uses', 'used_count',
            'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'used_count', 'created_at']


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating a coupon."""
    code = serializers.CharField(max_length=50)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2)


class CouponValidateResponseSerializer(serializers.Serializer):
    """Response serializer for coupon validation."""
    valid = serializers.BooleanField()
    message = serializers.CharField()
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    coupon = CouponSerializer(required=False)
