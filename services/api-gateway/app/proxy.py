"""
Proxy module for routing requests to downstream microservices.
"""
import logging
import httpx
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from .config import get_service_for_path

logger = logging.getLogger(__name__)


class ServiceProxy:
    """
    Proxy class for forwarding requests to downstream microservices.
    """

    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT

    async def forward_request(self, request) -> HttpResponse:
        """
        Forward the incoming request to the appropriate downstream service.

        Args:
            request: The Django request object

        Returns:
            HttpResponse with the downstream service's response
        """
        # Get the target service for this path
        service_url, prefix = get_service_for_path(request.path)

        if not service_url:
            return JsonResponse(
                {'error': 'No service found for this path'},
                status=404
            )

        # Build the target URL
        # Remove the API gateway prefix and forward to service
        target_path = request.path
        target_url = f"{service_url}{target_path}"

        # Add query string if present
        if request.META.get('QUERY_STRING'):
            target_url += f"?{request.META['QUERY_STRING']}"

        logger.info(f"Proxying {request.method} {request.path} -> {target_url}")

        # Build headers for downstream service
        headers = self._build_downstream_headers(request)

        # Get request body
        body = request.body if request.body else None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                )

                # Build response
                django_response = HttpResponse(
                    content=response.content,
                    status=response.status_code,
                    content_type=response.headers.get('content-type', 'application/json'),
                )

                # Copy relevant headers from downstream response
                headers_to_copy = [
                    'content-type',
                    'content-length',
                    'cache-control',
                    'etag',
                    'last-modified',
                    'x-request-id',
                    'location',
                ]

                for header in headers_to_copy:
                    if header in response.headers:
                        django_response[header] = response.headers[header]

                return django_response

        except httpx.TimeoutException:
            logger.error(f"Timeout while proxying to {target_url}")
            return JsonResponse(
                {'error': 'Service timeout'},
                status=504
            )
        except httpx.ConnectError:
            logger.error(f"Connection error while proxying to {target_url}")
            return JsonResponse(
                {'error': 'Service unavailable'},
                status=503
            )
        except Exception as e:
            logger.error(f"Error proxying request to {target_url}: {str(e)}")
            return JsonResponse(
                {'error': 'Internal gateway error'},
                status=500
            )

    def forward_request_sync(self, request) -> HttpResponse:
        """
        Synchronous version of forward_request for use with Django's sync views.

        Args:
            request: The Django request object

        Returns:
            HttpResponse with the downstream service's response
        """
        # Get the target service for this path
        service_url, prefix = get_service_for_path(request.path)

        if not service_url:
            return JsonResponse(
                {'error': 'No service found for this path'},
                status=404
            )

        # Build the target URL
        target_path = request.path
        target_url = f"{service_url}{target_path}"

        # Add query string if present
        if request.META.get('QUERY_STRING'):
            target_url += f"?{request.META['QUERY_STRING']}"

        logger.info(f"Proxying {request.method} {request.path} -> {target_url}")

        # Build headers for downstream service
        headers = self._build_downstream_headers(request)

        # Get request body
        body = request.body if request.body else None

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                )

                # Build response
                django_response = HttpResponse(
                    content=response.content,
                    status=response.status_code,
                    content_type=response.headers.get('content-type', 'application/json'),
                )

                # Copy relevant headers from downstream response
                headers_to_copy = [
                    'content-type',
                    'content-length',
                    'cache-control',
                    'etag',
                    'last-modified',
                    'x-request-id',
                    'location',
                ]

                for header in headers_to_copy:
                    if header in response.headers:
                        django_response[header] = response.headers[header]

                return django_response

        except httpx.TimeoutException:
            logger.error(f"Timeout while proxying to {target_url}")
            return JsonResponse(
                {'error': 'Service timeout'},
                status=504
            )
        except httpx.ConnectError:
            logger.error(f"Connection error while proxying to {target_url}")
            return JsonResponse(
                {'error': 'Service unavailable'},
                status=503
            )
        except Exception as e:
            logger.error(f"Error proxying request to {target_url}: {str(e)}")
            return JsonResponse(
                {'error': 'Internal gateway error'},
                status=500
            )

    def _build_downstream_headers(self, request) -> dict:
        """
        Build headers to send to downstream services.

        This includes:
        - Original request headers (filtered)
        - User info headers from JWT validation

        Args:
            request: The Django request object

        Returns:
            Dictionary of headers for downstream request
        """
        headers = {}

        # Headers to forward from original request
        forward_headers = [
            'content-type',
            'accept',
            'accept-language',
            'accept-encoding',
            'user-agent',
            'x-request-id',
            'x-forwarded-for',
            'x-real-ip',
        ]

        for header in forward_headers:
            django_header = f"HTTP_{header.upper().replace('-', '_')}"
            if django_header in request.META:
                headers[header] = request.META[django_header]
            elif header == 'content-type' and 'CONTENT_TYPE' in request.META:
                headers['content-type'] = request.META['CONTENT_TYPE']

        # Add user info headers from JWT validation
        if hasattr(request, 'user_id') and request.user_id:
            headers['X-User-Id'] = str(request.user_id)

        if hasattr(request, 'user_role') and request.user_role:
            headers['X-User-Role'] = request.user_role

        if hasattr(request, 'user_email') and request.user_email:
            headers['X-User-Email'] = request.user_email

        # Add forwarded headers
        client_ip = self._get_client_ip(request)
        if client_ip:
            existing_forwarded = headers.get('x-forwarded-for', '')
            if existing_forwarded:
                headers['x-forwarded-for'] = f"{existing_forwarded}, {client_ip}"
            else:
                headers['x-forwarded-for'] = client_ip

        # Forward the original Authorization header for services that need it
        auth_header = request.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header

        return headers

    def _get_client_ip(self, request) -> str:
        """
        Get the client's IP address from the request.

        Args:
            request: The Django request object

        Returns:
            The client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


# Singleton instance
proxy = ServiceProxy()
