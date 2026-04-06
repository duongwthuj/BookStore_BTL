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

# No relational database needed - using MongoDB for chat data
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
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'UNAUTHENTICATED_USER': None,
}

# Gemini settings
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash-lite')

# External service URLs
BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://book-service:8001')
ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8004')

# MongoDB settings
MONGODB_URL = os.environ.get('MONGODB_URL', 'mongodb://mongo:mongo@mongodb:27017/chatbot_db?authSource=admin')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'chatbot_db')

# Qdrant settings
QDRANT_HOST = os.environ.get('QDRANT_HOST', 'qdrant')
QDRANT_PORT = int(os.environ.get('QDRANT_PORT', '6333'))
QDRANT_COLLECTION = os.environ.get('QDRANT_COLLECTION', 'bookstore_knowledge')

# Embedding settings
EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'dangvantuan/vietnamese-document-embedding')
EMBEDDING_DIMENSION = int(os.environ.get('EMBEDDING_DIMENSION', '768'))

# RAG settings
RAG_TOP_K = int(os.environ.get('RAG_TOP_K', '5'))
RAG_SIMILARITY_THRESHOLD = float(os.environ.get('RAG_SIMILARITY_THRESHOLD', '0.3'))

# Chunking settings
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '512'))
CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '50'))
MIN_CHUNK_SIZE = int(os.environ.get('MIN_CHUNK_SIZE', '100'))

# System prompt for chatbot (RAG-enhanced)
CHATBOT_SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh của BookStore, được trang bị khả năng tìm kiếm thông tin từ cơ sở dữ liệu sách và tài liệu.

Nhiệm vụ của bạn:
- Tư vấn và gợi ý sách phù hợp dựa trên nhu cầu khách hàng
- Trả lời câu hỏi về thông tin sách (tác giả, giá, mô tả, thể loại...)
- Hướng dẫn đặt hàng, thanh toán (MoMo, COD), vận chuyển
- Giải đáp chính sách đổi trả, bảo hành
- Tra cứu trạng thái đơn hàng

Quy tắc:
- Trả lời dựa trên thông tin được cung cấp trong ngữ cảnh (context). Nếu không có thông tin liên quan, hãy nói rõ.
- Trả lời ngắn gọn, thân thiện, chuyên nghiệp bằng tiếng Việt.
- Khi giới thiệu sách, luôn kèm tên sách, tác giả và giá (nếu có).
- Nếu người dùng hỏi ngoài phạm vi, hãy lịch sự hướng dẫn họ liên hệ nhân viên."""
