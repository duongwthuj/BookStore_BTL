from django.contrib import admin
from .models import Order, OrderItem, Coupon


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['book_id', 'book_title', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id', 'status', 'total', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['id', 'customer_id', 'phone', 'shipping_address']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'max_uses', 'expires_at']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']
    ordering = ['-created_at']
