"""
Django settings for chatbot_service project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-chatbot-service-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'chatbot_service.urls'

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

WSGI_APPLICATION = 'chatbot_service.wsgi.application'

# No database needed - stateless service
DATABASES = {}

# Internationalization
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'UNAUTHENTICATED_USER': None,
}

# AI Provider settings
AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openai')  # 'openai', 'gemini' or 'ollama'

# OpenAI settings
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

# Gemini settings
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash-lite')

# Ollama settings (fallback)
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://ollama:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2:1b')

# External service URLs
BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://book-service:8001')
ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8004')

# System prompt for chatbot
CHATBOT_SYSTEM_PROMPT = """Bạn là trợ lý của BookStore. Hãy trả lời các câu hỏi về:
- Giới thiệu cửa hàng
- Hướng dẫn đặt hàng
- Thanh toán (MoMo, COD)
- Vận chuyển
- Chính sách đổi trả
- Tra cứu sách
- Tra cứu đơn hàng
Trả lời ngắn gọn, thân thiện bằng tiếng Việt."""
