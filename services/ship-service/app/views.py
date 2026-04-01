from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django.shortcuts import get_object_or_404

from .models import ShippingMethod, Shipment
from .serializers import (
    ShippingMethodSerializer,
    ShipmentSerializer,
    ShipmentCreateSerializer,
    ShipmentStatusUpdateSerializer,
)
from .services import order_service_client


class ShippingMethodListCreateView(ListCreateAPIView):
    """
    GET /shipping/methods/ - List all active shipping methods
    POST /shipping/methods/ - Create a new shipping method (Manager)
    """
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer


class ShippingMethodDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET /shipping/methods/{id}/ - Retrieve a shipping method
    PUT /shipping/methods/{id}/ - Update a shipping method
    DELETE /shipping/methods/{id}/ - Delete (deactivate) a shipping method
    """
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer

    def perform_destroy(self, instance):
        # Soft delete - just deactivate
        instance.is_active = False
        instance.save()


class ShippingCalculateView(APIView):
    """
    GET /shipping/calculate/?subtotal=&method_id= - Calculate shipping fee
    """

    def get(self, request):
        subtotal = request.query_params.get('subtotal')
        method_id = request.query_params.get('method_id')

        if not subtotal or not method_id:
            return Response(
                {'error': 'Both subtotal and method_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subtotal = Decimal(subtotal)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid subtotal value'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            method = ShippingMethod.objects.get(id=method_id, is_active=True)
        except ShippingMethod.DoesNotExist:
            return Response(
                {'error': 'Shipping method not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calculate fee - check for free shipping threshold
        if method.free_ship_threshold and subtotal >= method.free_ship_threshold:
            shipping_fee = Decimal('0.00')
            free_shipping = True
        else:
            shipping_fee = method.fee
            free_shipping = False

        return Response({
            'method_id': method.id,
            'method_name': method.name,
            'subtotal': str(subtotal),
            'shipping_fee': str(shipping_fee),
            'free_shipping': free_shipping,
            'free_ship_threshold': str(method.free_ship_threshold) if method.free_ship_threshold else None,
            'estimated_days': method.estimated_days,
            'total': str(subtotal + shipping_fee),
        })


class ShipmentCreateView(APIView):
    """
    POST /shipments/ - Create shipment for order
    """

    def post(self, request):
        serializer = ShipmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']

        # Check if shipment already exists for this order
        if Shipment.objects.filter(order_id=order_id).exists():
            return Response(
                {'error': 'Shipment already exists for this order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shipment = Shipment.objects.create(**serializer.validated_data)

        # Notify order service about shipment creation
        order_service_client.update_order_shipping_status(order_id, 'pending')

        return Response(
            ShipmentSerializer(shipment).data,
            status=status.HTTP_201_CREATED
        )


class ShipmentByOrderView(APIView):
    """
    GET /shipments/{order_id}/ - Get shipment by order ID
    """

    def get(self, request, order_id):
        shipment = get_object_or_404(Shipment, order_id=order_id)
        return Response(ShipmentSerializer(shipment).data)


class ShipmentStatusUpdateView(APIView):
    """
    PUT /shipments/{id}/status/ - Update shipment status (Staff)
    """

    def put(self, request, pk):
        shipment = get_object_or_404(Shipment, pk=pk)
        serializer = ShipmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        old_status = shipment.status

        # Update status and timestamps
        shipment.status = new_status

        if new_status == 'picked_up' and not shipment.shipped_at:
            shipment.shipped_at = timezone.now()
        elif new_status == 'delivered' and not shipment.delivered_at:
            shipment.delivered_at = timezone.now()

        shipment.save()

        # Notify order service about status change
        order_service_client.update_order_shipping_status(shipment.order_id, new_status)

        return Response({
            'message': f'Status updated from {old_status} to {new_status}',
            'shipment': ShipmentSerializer(shipment).data
        })


class ShipmentTrackView(APIView):
    """
    GET /shipments/track/{tracking_code}/ - Track shipment by tracking code
    """

    def get(self, request, tracking_code):
        shipment = get_object_or_404(Shipment, tracking_code=tracking_code)

        # Build tracking history based on status
        tracking_info = {
            'tracking_code': shipment.tracking_code,
            'order_id': shipment.order_id,
            'status': shipment.status,
            'status_display': shipment.get_status_display(),
            'method': shipment.method.name,
            'estimated_days': shipment.method.estimated_days,
            'created_at': shipment.created_at,
            'shipped_at': shipment.shipped_at,
            'delivered_at': shipment.delivered_at,
        }

        # Build timeline
        timeline = [
            {
                'status': 'pending',
                'label': 'Order Placed',
                'timestamp': shipment.created_at,
                'completed': True,
            }
        ]

        if shipment.status in ['picked_up', 'in_transit', 'delivered']:
            timeline.append({
                'status': 'picked_up',
                'label': 'Picked Up',
                'timestamp': shipment.shipped_at,
                'completed': True,
            })

        if shipment.status in ['in_transit', 'delivered']:
            timeline.append({
                'status': 'in_transit',
                'label': 'In Transit',
                'timestamp': shipment.shipped_at,  # Same as picked up for now
                'completed': True,
            })

        if shipment.status == 'delivered':
            timeline.append({
                'status': 'delivered',
                'label': 'Delivered',
                'timestamp': shipment.delivered_at,
                'completed': True,
            })

        tracking_info['timeline'] = timeline

        return Response(tracking_info)
