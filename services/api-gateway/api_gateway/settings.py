"""
Django settings for api_gateway project.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-api-gateway-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,api-gateway').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'app.middleware.JWTAuthenticationMiddleware',
]

ROOT_URLCONF = 'api_gateway.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'api_gateway.wsgi.application'

# No database needed for API Gateway
DATABASES = {}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1', 'yes')
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get('CORS_ALLOWED_ORIGINS') else []
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# JWT Settings - must match auth-service SECRET_KEY for token validation
JWT_SECRET = os.environ.get('JWT_SECRET', 'django-insecure-dev-key-change-in-production')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

# Service URLs - all services run on port 8000 internally
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth-service:8000')
CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:8000')
STAFF_SERVICE_URL = os.environ.get('STAFF_SERVICE_URL', 'http://staff-service:8000')
MANAGER_SERVICE_URL = os.environ.get('MANAGER_SERVICE_URL', 'http://manager-service:8000')
CATALOG_SERVICE_URL = os.environ.get('CATALOG_SERVICE_URL', 'http://catalog-service:8000')
BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://book-service:8000')
CART_SERVICE_URL = os.environ.get('CART_SERVICE_URL', 'http://cart-service:8000')
ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8000')
PAY_SERVICE_URL = os.environ.get('PAY_SERVICE_URL', 'http://pay-service:8000')
SHIP_SERVICE_URL = os.environ.get('SHIP_SERVICE_URL', 'http://ship-service:8000')
COMMENT_RATE_SERVICE_URL = os.environ.get('COMMENT_RATE_SERVICE_URL', 'http://comment-rate-service:8000')
RECOMMENDER_SERVICE_URL = os.environ.get('RECOMMENDER_SERVICE_URL', 'http://recommender-service:8000')
CHATBOT_SERVICE_URL = os.environ.get('CHATBOT_SERVICE_URL', 'http://chatbot-service:8000')

# Request timeout in seconds (longer for AI services like chatbot)
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '120'))

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
