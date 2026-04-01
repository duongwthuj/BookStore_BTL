from django.urls import path
from .views import (
    MoMoCreateView,
    MoMoCallbackView,
    MoMoReturnView,
    CODCreateView,
    PaymentStatusView,
    CODConfirmView,
)

urlpatterns = [
    # MoMo endpoints
    path('momo/create/', MoMoCreateView.as_view(), name='momo-create'),
    path('momo/callback/', MoMoCallbackView.as_view(), name='momo-callback'),
    path('momo/return/', MoMoReturnView.as_view(), name='momo-return'),

    # COD endpoints
    path('cod/create/', CODCreateView.as_view(), name='cod-create'),

    # Payment status
    path('<int:order_id>/', PaymentStatusView.as_view(), name='payment-status'),
    path('<int:order_id>/confirm/', CODConfirmView.as_view(), name='cod-confirm'),
]
