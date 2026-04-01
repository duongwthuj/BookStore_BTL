"""
URL configuration for the app.
"""
from django.urls import path, re_path

from .views import GatewayProxyView, HealthCheckView, ServiceStatusView

urlpatterns = [
    # Health check endpoint
    path('health/', HealthCheckView.as_view(), name='health'),

    # Service status endpoint (for debugging)
    path('status/', ServiceStatusView.as_view(), name='status'),

    # Catch-all proxy for all API routes
    # This must be last to allow specific routes above to match first
    re_path(r'^(?P<path>.*)$', GatewayProxyView.as_view(), name='gateway-proxy'),
]
