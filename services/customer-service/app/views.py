from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer
from .services import cart_service_client


@api_view(['GET', 'POST'])
def customer_list(request):
    """
    GET: List all customers.
    POST: Create a new customer and trigger cart creation.
    """
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()

            # Trigger cart creation via cart-service
            cart_data = cart_service_client.create_cart(customer.id)

            response_data = serializer.data
            if cart_data:
                response_data['cart'] = cart_data

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def customer_detail(request, pk):
    """
    GET: Retrieve a customer.
    PUT: Update a customer.
    DELETE: Delete a customer.
    """
    try:
        customer = Customer.objects.get(pk=pk)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def customer_by_user(request, user_id):
    """
    GET: Retrieve a customer by user_id.
    """
    try:
        customer = Customer.objects.get(user_id=user_id)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CustomerSerializer(customer)
    return Response(serializer.data)
