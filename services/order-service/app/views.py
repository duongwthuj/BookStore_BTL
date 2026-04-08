from decimal import Decimal
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem, Coupon
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
    CouponSerializer,
    CouponValidateSerializer,
)
from .services import book_service, recommender_service, ServiceException


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order management."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.prefetch_related('items').all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by customer_id
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create an order (checkout from cart)."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        items = data.get('items', [])
        if not items:
            return Response(
                {"error": "No items provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate subtotal
        subtotal = Decimal('0')
        for item in items:
            subtotal += Decimal(str(item['price'])) * item['quantity']

        # Apply coupon if provided
        discount = Decimal('0')
        coupon_code = data.get('coupon_code', '')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                is_valid, message = coupon.is_valid(subtotal)
                if is_valid:
                    discount = coupon.calculate_discount(subtotal)
                    # Increment used count
                    coupon.used_count += 1
                    coupon.save()
            except Coupon.DoesNotExist:
                pass  # Invalid coupon code, ignore

        # Calculate total
        shipping_fee = Decimal(str(data.get('shipping_fee', 0)))
        total = subtotal - discount + shipping_fee

        # Create order
        order = Order.objects.create(
            customer_id=data['customer_id'],
            shipping_address=data['shipping_address'],
            phone=data['phone'],
            note=data.get('note', ''),
            coupon_code=coupon_code,
            payment_method=data['payment_method'],
            shipping_method=data['shipping_method'],
            shipping_fee=shipping_fee,
            subtotal=subtotal,
            discount=discount,
            total=total,
        )

        # Create order items
        order_items = []
        for item in items:
            order_items.append(OrderItem(
                order=order,
                book_id=item['book_id'],
                book_title=item['book_title'],
                quantity=item['quantity'],
                price=Decimal(str(item['price'])),
            ))
        OrderItem.objects.bulk_create(order_items)

        # Update stock in book-service
        try:
            book_service.bulk_update_stock([
                {'book_id': item['book_id'], 'quantity': item['quantity']}
                for item in items
            ])
        except ServiceException as e:
            # Log error but don't fail the order
            pass

        # Record purchase interactions for recommender system
        book_ids = [item['book_id'] for item in items]
        recommender_service.record_purchase(data['customer_id'], book_ids)

        # Return created order
        order.refresh_from_db()
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, pk=None):
        """Update order status (Staff only)."""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        old_status = order.status

        # Validate status transition
        valid_transitions = {
            'pending': ['paid', 'cancelled'],
            'paid': ['shipping', 'cancelled'],
            'shipping': ['delivered', 'cancelled'],
            'delivered': ['completed'],
            'completed': [],
            'cancelled': [],
        }

        if new_status not in valid_transitions.get(old_status, []):
            return Response(
                {"error": f"Cannot transition from '{old_status}' to '{new_status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If cancelling, restore stock
        if new_status == 'cancelled' and old_status != 'cancelled':
            try:
                for item in order.items.all():
                    book_service.update_stock(item.book_id, item.quantity)  # Restore stock
            except ServiceException:
                pass  # Log but continue

        order.status = new_status
        order.save()

        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data)

    @action(detail=False, methods=['get'], url_path='customer/(?P<customer_id>[^/.]+)')
    def by_customer(self, request, customer_id=None):
        """Get orders by customer ID."""
        orders = self.get_queryset().filter(customer_id=customer_id)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Get order statistics for dashboard."""
        # Date range filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = Order.objects.all()
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Overall stats
        total_orders = queryset.count()
        total_revenue = queryset.filter(
            status__in=['paid', 'shipping', 'delivered', 'completed']
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')

        avg_order_value = queryset.filter(
            status__in=['paid', 'shipping', 'delivered', 'completed']
        ).aggregate(avg=Avg('total'))['avg'] or Decimal('0')

        # Orders by status
        orders_by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        # Orders by date (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        orders_by_date = queryset.filter(
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            revenue=Sum('total')
        ).order_by('date')

        # Monthly stats
        orders_by_month = queryset.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            revenue=Sum('total')
        ).order_by('-month')[:12]

        # Top products
        top_products = OrderItem.objects.filter(
            order__in=queryset
        ).values('book_id', 'book_title').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_quantity')[:10]

        return Response({
            'total_orders': total_orders,
            'total_revenue': str(total_revenue),
            'avg_order_value': str(round(avg_order_value, 2)),
            'orders_by_status': list(orders_by_status),
            'orders_by_date': [
                {
                    'date': item['date'].isoformat() if item['date'] else None,
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0)
                }
                for item in orders_by_date
            ],
            'orders_by_month': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0)
                }
                for item in orders_by_month
            ],
            'top_products': list(top_products),
        })


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for Coupon management."""
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_queryset(self):
        queryset = Coupon.objects.all()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='validate')
    def validate(self, request):
        """Validate a coupon code."""
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        order_total = serializer.validated_data['order_total']

        try:
            coupon = Coupon.objects.get(code=code)
            is_valid, message = coupon.is_valid(order_total)

            if is_valid:
                discount = coupon.calculate_discount(order_total)
                return Response({
                    'valid': True,
                    'message': message,
                    'discount': str(discount),
                    'coupon': CouponSerializer(coupon).data
                })
            else:
                return Response({
                    'valid': False,
                    'message': message
                })
        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'message': 'Coupon not found'
            })
