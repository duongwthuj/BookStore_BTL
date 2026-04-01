from rest_framework import serializers
from .models import ShippingMethod, Shipment


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = [
            'id',
            'name',
            'fee',
            'estimated_days',
            'free_ship_threshold',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShipmentSerializer(serializers.ModelSerializer):
    method_name = serializers.CharField(source='method.name', read_only=True)
    method_fee = serializers.DecimalField(
        source='method.fee',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Shipment
        fields = [
            'id',
            'order_id',
            'method',
            'method_name',
            'method_fee',
            'status',
            'tracking_code',
            'shipped_at',
            'delivered_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'tracking_code', 'created_at', 'updated_at']


class ShipmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['order_id', 'method']


class ShipmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipment.STATUS_CHOICES)


class ShippingCalculateSerializer(serializers.Serializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    method_id = serializers.IntegerField()
