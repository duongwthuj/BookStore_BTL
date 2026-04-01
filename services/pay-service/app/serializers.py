from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'method',
            'amount',
            'status',
            'transaction_id',
            'paid_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'transaction_id', 'paid_at', 'created_at', 'updated_at']


class MoMoCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_info = serializers.CharField(max_length=255, required=False, default='Payment for order')


class MoMoCallbackSerializer(serializers.Serializer):
    partnerCode = serializers.CharField()
    orderId = serializers.CharField()
    requestId = serializers.CharField()
    amount = serializers.IntegerField()
    orderInfo = serializers.CharField()
    orderType = serializers.CharField()
    transId = serializers.IntegerField()
    resultCode = serializers.IntegerField()
    message = serializers.CharField()
    payType = serializers.CharField()
    responseTime = serializers.IntegerField()
    extraData = serializers.CharField(allow_blank=True)
    signature = serializers.CharField()


class CODCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'method',
            'amount',
            'status',
            'transaction_id',
            'paid_at',
            'created_at',
            'updated_at',
        ]
