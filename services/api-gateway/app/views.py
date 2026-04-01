"""
Views for API Gateway.
"""
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .proxy import proxy

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class GatewayProxyView(View):
    """
    Main proxy view that forwards all API requests to downstream services.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Handle all HTTP methods and forward to the appropriate service.
        """
        return proxy.forward_request_sync(request)


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """
    Health check endpoint for the API Gateway.
    """

    def get(self, request):
        """
        Return health status of the API Gateway.
        """
        return JsonResponse({
            'status': 'healthy',
            'service': 'api-gateway',
        })


@method_decorator(csrf_exempt, name='dispatch')
class ServiceStatusView(View):
    """
    View to check the status of downstream services.
    """

    def get(self, request):
        """
        Return the routing configuration (for debugging purposes).
        """
        from .config import ROUTING_TABLE

        services = {}
        for name, config in ROUTING_TABLE.items():
            services[name] = {
                'url': config['url'],
                'prefix': config['prefix'],
            }

        return JsonResponse({
            'gateway': 'api-gateway',
            'services': services,
        })
