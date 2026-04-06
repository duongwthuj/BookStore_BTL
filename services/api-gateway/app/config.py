"""
Configuration for API Gateway routing and authentication.
"""
from django.conf import settings

# Service routing configuration
ROUTING_TABLE = {
    'auth': {
        'url': settings.AUTH_SERVICE_URL,
        'prefix': '/api/auth/',
    },
    'customers': {
        'url': settings.CUSTOMER_SERVICE_URL,
        'prefix': '/api/customers/',
    },
    'staff': {
        'url': settings.STAFF_SERVICE_URL,
        'prefix': '/api/staff/',
    },
    'managers': {
        'url': settings.MANAGER_SERVICE_URL,
        'prefix': '/api/managers/',
    },
    'categories': {
        'url': settings.CATALOG_SERVICE_URL,
        'prefix': '/api/categories/',
    },
    'collections': {
        'url': settings.CATALOG_SERVICE_URL,
        'prefix': '/api/collections/',
    },
    'books': {
        'url': settings.BOOK_SERVICE_URL,
        'prefix': '/api/books/',
    },
    'cart': {
        'url': settings.CART_SERVICE_URL,
        'prefix': '/api/cart/',
    },
    'carts': {
        'url': settings.CART_SERVICE_URL,
        'prefix': '/api/carts/',
    },
    'orders': {
        'url': settings.ORDER_SERVICE_URL,
        'prefix': '/api/orders/',
    },
    'coupons': {
        'url': settings.ORDER_SERVICE_URL,
        'prefix': '/api/coupons/',
    },
    'payments': {
        'url': settings.PAY_SERVICE_URL,
        'prefix': '/api/payments/',
    },
    'shipping': {
        'url': settings.SHIP_SERVICE_URL,
        'prefix': '/api/shipping/',
    },
    'shipments': {
        'url': settings.SHIP_SERVICE_URL,
        'prefix': '/api/shipments/',
    },
    'reviews': {
        'url': settings.COMMENT_RATE_SERVICE_URL,
        'prefix': '/api/reviews/',
    },
    'recommend': {
        'url': settings.RECOMMENDER_SERVICE_URL,
        'prefix': '/api/recommend/',
    },
    'chat': {
        'url': settings.CHATBOT_SERVICE_URL,
        'prefix': '/api/chat/',
    },
}

# Public endpoints that don't require authentication
# Format: (path_pattern, methods) - methods is a list or None for all methods
PUBLIC_ENDPOINTS = [
    # Auth endpoints
    ('/api/auth/register/', ['POST']),
    ('/api/auth/login/', ['POST']),
    ('/api/auth/refresh/', ['POST']),

    # Book endpoints (read-only)
    ('/api/books/', ['GET']),
    ('/api/books/{id}/', ['GET']),

    # Category and collection endpoints (read-only)
    ('/api/categories/', ['GET']),
    ('/api/categories/{id}/', ['GET']),
    ('/api/collections/', ['GET']),
    ('/api/collections/{id}/', ['GET']),

    # Reviews for books (read-only)
    ('/api/reviews/book/{id}/', ['GET']),

    # Recommendations (all GET requests)
    ('/api/recommend/', None),  # None means all methods

    # Chatbot (all requests)
    ('/api/chat/', None),

    # Shipping methods (read-only)
    ('/api/shipping/methods/', ['GET']),

    # Payment gateway callbacks/redirects (must be public)
    ('/api/payments/momo/return/', ['GET']),
    ('/api/payments/momo/callback/', ['POST']),
]


def is_public_endpoint(path: str, method: str) -> bool:
    """
    Check if a given path and method combination is a public endpoint.

    Args:
        path: The request path (e.g., '/api/auth/login/')
        method: The HTTP method (e.g., 'GET', 'POST')

    Returns:
        True if the endpoint is public, False otherwise
    """
    # Normalize path - ensure trailing slash
    if not path.endswith('/'):
        path = path + '/'

    method = method.upper()

    for pattern, allowed_methods in PUBLIC_ENDPOINTS:
        if _path_matches_pattern(path, pattern):
            # If allowed_methods is None, all methods are allowed
            if allowed_methods is None:
                return True
            # Otherwise, check if the method is in the allowed list
            if method in allowed_methods:
                return True

    return False


def _path_matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches a pattern with optional {id} placeholders.

    Args:
        path: The actual request path
        pattern: The pattern to match against (may contain {id} or similar)

    Returns:
        True if the path matches the pattern
    """
    # Handle patterns that end with {id}/
    if '{' in pattern:
        # Split pattern into prefix and suffix around the placeholder
        parts = pattern.split('{')
        prefix = parts[0]

        # Check if path starts with the prefix
        if not path.startswith(prefix):
            return False

        # For patterns like /api/books/{id}/, check if path matches
        # Path should be prefix + some_id + /
        remainder = path[len(prefix):]

        # If the pattern has more after the placeholder
        if '}/' in parts[1]:
            suffix = parts[1].split('}/')[1]
            if suffix:
                # Path should end with the suffix
                if not remainder.endswith(suffix):
                    return False
                # Extract the ID part
                id_part = remainder[:-len(suffix) - 1] if suffix else remainder[:-1]
            else:
                # Pattern ends with {id}/
                id_part = remainder.rstrip('/')

            # ID should not be empty and should not contain /
            return bool(id_part) and '/' not in id_part

        return True

    # Exact match or prefix match for wildcard patterns
    if pattern.endswith('/'):
        # For patterns like /api/recommend/, also match sub-paths
        return path == pattern or path.startswith(pattern)

    return path == pattern


def get_service_for_path(path: str) -> tuple:
    """
    Get the service URL and path prefix for a given request path.

    Args:
        path: The request path (e.g., '/api/auth/login/')

    Returns:
        Tuple of (service_url, prefix) or (None, None) if no match
    """
    for service_name, config in ROUTING_TABLE.items():
        prefix = config['prefix']
        if path.startswith(prefix):
            return config['url'], prefix

    return None, None
