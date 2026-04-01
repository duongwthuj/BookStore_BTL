"""
Views for payment operations
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from django.conf import settings

from .models import Payment
from .serializers import (
    MoMoCreateSerializer,
    MoMoCallbackSerializer,
    CODCreateSerializer,
    PaymentStatusSerializer,
)
from .momo import momo_client
from .services import payment_service


class MoMoCreateView(APIView):
    """
    POST /payments/momo/create/
    Create a MoMo payment and return payment URL
    """

    def post(self, request):
        serializer = MoMoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        amount = serializer.validated_data['amount']
        order_info = serializer.validated_data.get('order_info', f'Payment for order #{order_id}')

        try:
            # Create payment record
            payment = payment_service.create_momo_payment(order_id, float(amount), order_info)

            # Call MoMo API
            momo_response = momo_client.create_payment(
                order_id=order_id,
                amount=int(amount),  # MoMo requires integer amount
                order_info=order_info
            )

            if momo_response.get('resultCode') == 0:
                return Response({
                    'payment_id': payment.id,
                    'order_id': order_id,
                    'pay_url': momo_response.get('payUrl'),
                    'qr_code_url': momo_response.get('qrCodeUrl'),
                    'deeplink': momo_response.get('deeplink'),
                    'message': 'Payment created successfully'
                }, status=status.HTTP_201_CREATED)
            else:
                # Mark payment as failed if MoMo API returns error
                payment.status = 'failed'
                payment.save()
                return Response({
                    'error': momo_response.get('message', 'Failed to create MoMo payment'),
                    'result_code': momo_response.get('resultCode')
                }, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MoMoCallbackView(APIView):
    """
    POST /payments/momo/callback/
    Handle MoMo IPN (Instant Payment Notification)
    """

    def post(self, request):
        serializer = MoMoCallbackSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        callback_data = serializer.validated_data

        # Verify signature
        if not momo_client.verify_callback_signature(request.data):
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Parse order ID from MoMo order ID format
        momo_order_id = callback_data['orderId']
        order_id = momo_client.parse_order_id(momo_order_id)

        if order_id == 0:
            return Response(
                {'error': 'Invalid order ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Process the callback
            payment = payment_service.process_momo_callback(
                order_id=order_id,
                result_code=callback_data['resultCode'],
                transaction_id=callback_data['transId']
            )

            return Response({
                'status': 'ok',
                'payment_status': payment.status,
                'order_id': order_id
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MoMoReturnView(APIView):
    """
    GET /payments/momo/return/
    Handle return URL after MoMo payment (user redirect)
    """

    def get(self, request):
        result_code = request.query_params.get('resultCode')
        momo_order_id = request.query_params.get('orderId')
        message = request.query_params.get('message', '')

        if momo_order_id:
            order_id = momo_client.parse_order_id(momo_order_id)
        else:
            order_id = 0

        # This endpoint is typically used to redirect user to frontend
        # For API purposes, return payment result
        if result_code == '0':
            return Response({
                'status': 'success',
                'message': 'Payment completed successfully',
                'order_id': order_id
            })
        else:
            return Response({
                'status': 'failed',
                'message': message or 'Payment failed',
                'result_code': result_code,
                'order_id': order_id
            })


class CODCreateView(APIView):
    """
    POST /payments/cod/create/
    Create a COD (Cash on Delivery) payment
    """

    def post(self, request):
        serializer = CODCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data['order_id']
        amount = serializer.validated_data['amount']

        try:
            payment = payment_service.create_cod_payment(order_id, float(amount))
            return Response({
                'payment_id': payment.id,
                'order_id': order_id,
                'method': 'cod',
                'amount': str(payment.amount),
                'status': payment.status,
                'message': 'COD payment created. Pay upon delivery.'
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentStatusView(APIView):
    """
    GET /payments/{order_id}/
    Get payment status for an order
    """

    def get(self, request, order_id):
        payment = payment_service.get_payment_by_order(order_id)

        if not payment:
            return Response(
                {'error': f'No payment found for order {order_id}'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PaymentStatusSerializer(payment)
        return Response(serializer.data)


class CODConfirmView(APIView):
    """
    PUT /payments/{order_id}/confirm/
    Confirm COD payment (Staff only)
    """

    def put(self, request, order_id):
        try:
            payment = payment_service.confirm_cod_payment(order_id)
            return Response({
                'payment_id': payment.id,
                'order_id': order_id,
                'status': payment.status,
                'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
                'message': 'COD payment confirmed successfully'
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
