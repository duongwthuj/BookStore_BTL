from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartCreateSerializer,
    CartItemSerializer,
    CartItemCreateSerializer,
    CartItemUpdateSerializer,
)
from .services import book_service, BookServiceError


def get_user_id_from_request(request):
    """Extract user ID from X-User-Id header set by API Gateway."""
    user_id = request.headers.get('X-User-Id') or request.META.get('HTTP_X_USER_ID')
    if user_id:
        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None
    return None


def get_or_create_cart(customer_id):
    """Get or create cart for a customer."""
    cart, created = Cart.objects.get_or_create(customer_id=customer_id)
    return cart


# ==================== New simplified endpoints (JWT based) ====================

@api_view(['GET'])
def get_my_cart(request):
    """
    Get cart with all items for the current user.
    GET /api/cart/
    """
    customer_id = get_user_id_from_request(request)
    if not customer_id:
        return Response(
            {'error': 'Unauthorized'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    cart = get_or_create_cart(customer_id)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
def add_my_item(request):
    """
    Add a book to the current user's cart.
    POST /api/cart/items/
    """
    customer_id = get_user_id_from_request(request)
    if not customer_id:
        return Response(
            {'error': 'Unauthorized'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    cart = get_or_create_cart(customer_id)

    serializer = CartItemCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    book_id = serializer.validated_data['book_id']
    quantity = serializer.validated_data['quantity']

    # Get book info from book-service
    try:
        book_info = book_service.get_book(book_id)
        price = book_info.get('price', 0)
    except BookServiceError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Check if item already exists in cart
    existing_item = CartItem.objects.filter(cart=cart, book_id=book_id).first()
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        existing_item.price = Decimal(str(price))
        existing_item.save()
        return Response(CartItemSerializer(existing_item).data)

    # Create new cart item
    cart_item = CartItem.objects.create(
        cart=cart,
        book_id=book_id,
        quantity=quantity,
        price=Decimal(str(price))
    )
    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
def my_item_detail(request, item_id):
    """
    Update or remove a cart item for the current user.
    PUT /api/cart/items/{item_id}/ - Update quantity
    DELETE /api/cart/items/{item_id}/ - Remove item
    """
    customer_id = get_user_id_from_request(request)
    if not customer_id:
        return Response(
            {'error': 'Unauthorized'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        cart = Cart.objects.get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'PUT':
        serializer = CartItemUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

    elif request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def clear_my_cart(request):
    """
    Clear all items from the current user's cart.
    DELETE /api/cart/clear/
    """
    customer_id = get_user_id_from_request(request)
    if not customer_id:
        return Response(
            {'error': 'Unauthorized'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        cart = Cart.objects.get(customer_id=customer_id)
        cart.items.all().delete()
    except Cart.DoesNotExist:
        pass  # No cart to clear

    return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== Legacy endpoints with customer_id in URL ====================

@api_view(['POST'])
def create_cart(request):
    """
    Create a new cart for a customer.
    POST /carts/
    """
    serializer = CartCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    customer_id = serializer.validated_data['customer_id']

    # Check if cart already exists for this customer
    if Cart.objects.filter(customer_id=customer_id).exists():
        return Response(
            {'error': 'Cart already exists for this customer'},
            status=status.HTTP_400_BAD_REQUEST
        )

    cart = Cart.objects.create(customer_id=customer_id)
    return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_cart(request, customer_id):
    """
    Get cart with all items for a customer.
    GET /carts/{customer_id}/
    """
    try:
        cart = Cart.objects.prefetch_related('items').get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found for this customer'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(CartSerializer(cart).data)


@api_view(['POST'])
def add_item(request, customer_id):
    """
    Add a book to the cart.
    POST /carts/{customer_id}/items/
    """
    try:
        cart = Cart.objects.get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found for this customer'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CartItemCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    book_id = serializer.validated_data['book_id']
    quantity = serializer.validated_data['quantity']

    # Get book price from book-service
    try:
        price = book_service.get_book_price(book_id)
    except BookServiceError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Check if item already exists in cart
    existing_item = CartItem.objects.filter(cart=cart, book_id=book_id).first()
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        existing_item.price = Decimal(str(price))  # Update to latest price
        existing_item.save()
        return Response(CartItemSerializer(existing_item).data)

    # Create new cart item
    cart_item = CartItem.objects.create(
        cart=cart,
        book_id=book_id,
        quantity=quantity,
        price=Decimal(str(price))
    )
    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
def item_detail(request, customer_id, item_id):
    """
    Update or remove a cart item.
    PUT /carts/{customer_id}/items/{item_id}/ - Update quantity
    DELETE /carts/{customer_id}/items/{item_id}/ - Remove item
    """
    try:
        cart = Cart.objects.get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found for this customer'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'PUT':
        serializer = CartItemUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

    elif request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def clear_cart(request, customer_id):
    """
    Clear all items from the cart.
    DELETE /carts/{customer_id}/clear/
    """
    try:
        cart = Cart.objects.get(customer_id=customer_id)
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found for this customer'},
            status=status.HTTP_404_NOT_FOUND
        )

    cart.items.all().delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
