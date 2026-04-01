"""
JWT Authentication Middleware for API Gateway.
"""
import logging
import jwt
from django.conf import settings
from django.http import JsonResponse

from .config import is_public_endpoint

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    """
    Middleware to validate JWT tokens and extract user information.

    This middleware:
    1. Checks if the endpoint is public (no auth required)
    2. Extracts JWT from Authorization header
    3. Validates the token locally using the shared secret
    4. Adds user info to the request for downstream services
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_secret = settings.JWT_SECRET
        self.jwt_algorithm = settings.JWT_ALGORITHM

    def __call__(self, request):
        # Skip authentication for non-API paths
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Check if this is a public endpoint
        if is_public_endpoint(request.path, request.method):
            logger.debug(f"Public endpoint accessed: {request.method} {request.path}")
            # Still try to extract user info if token is provided (optional auth)
            self._try_extract_user_info(request)
            return self.get_response(request)

        # Extract and validate JWT token
        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            return JsonResponse(
                {'error': 'Authorization header is required'},
                status=401
            )

        # Check for Bearer token format
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {'error': 'Invalid authorization header format. Expected: Bearer <token>'},
                status=401
            )

        token = auth_header[7:]  # Remove 'Bearer ' prefix

        # Validate token
        try:
            payload = self._validate_token(token)

            # Add user info to request for views and downstream services
            request.user_id = payload.get('user_id') or payload.get('sub')
            request.user_role = payload.get('role', 'customer')
            request.user_email = payload.get('email')
            request.jwt_payload = payload

            logger.debug(f"Authenticated user: {request.user_id} with role: {request.user_role}")

        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token used for {request.path}")
            return JsonResponse(
                {'error': 'Token has expired'},
                status=401
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token for {request.path}: {str(e)}")
            return JsonResponse(
                {'error': 'Invalid token'},
                status=401
            )
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return JsonResponse(
                {'error': 'Authentication failed'},
                status=401
            )

        return self.get_response(request)

    def _validate_token(self, token: str) -> dict:
        """
        Validate JWT token and return payload.

        Args:
            token: The JWT token string

        Returns:
            The decoded token payload

        Raises:
            jwt.InvalidTokenError: If the token is invalid
        """
        payload = jwt.decode(
            token,
            self.jwt_secret,
            algorithms=[self.jwt_algorithm]
        )
        return payload

    def _try_extract_user_info(self, request):
        """
        Try to extract user info from token for public endpoints.
        This allows optional authentication on public endpoints.

        Args:
            request: The Django request object
        """
        request.user_id = None
        request.user_role = None
        request.user_email = None
        request.jwt_payload = None

        auth_header = request.headers.get('Authorization', '')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = self._validate_token(token)
                request.user_id = payload.get('user_id') or payload.get('sub')
                request.user_role = payload.get('role', 'customer')
                request.user_email = payload.get('email')
                request.jwt_payload = payload
            except Exception:
                # For public endpoints, ignore invalid tokens
                pass
