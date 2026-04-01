from django.contrib import admin
from .models import ShippingMethod, Shipment


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'fee', 'estimated_days', 'free_ship_threshold', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_code', 'order_id', 'method', 'status', 'shipped_at', 'delivered_at', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['tracking_code', 'order_id']
    readonly_fields = ['tracking_code', 'created_at', 'updated_at']
