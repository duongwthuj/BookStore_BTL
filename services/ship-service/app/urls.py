from django.urls import path
from .views import (
    ShippingMethodListCreateView,
    ShippingMethodDetailView,
    ShippingCalculateView,
    ShipmentCreateView,
    ShipmentByOrderView,
    ShipmentStatusUpdateView,
    ShipmentTrackView,
)

urlpatterns = [
    # Shipping Methods
    path('shipping/methods/', ShippingMethodListCreateView.as_view(), name='shipping-method-list'),
    path('shipping/methods/<int:pk>/', ShippingMethodDetailView.as_view(), name='shipping-method-detail'),
    path('shipping/calculate/', ShippingCalculateView.as_view(), name='shipping-calculate'),

    # Shipments
    path('shipments/', ShipmentCreateView.as_view(), name='shipment-create'),
    path('shipments/<int:order_id>/', ShipmentByOrderView.as_view(), name='shipment-by-order'),
    path('shipments/<int:pk>/status/', ShipmentStatusUpdateView.as_view(), name='shipment-status-update'),
    path('shipments/track/<str:tracking_code>/', ShipmentTrackView.as_view(), name='shipment-track'),
]
