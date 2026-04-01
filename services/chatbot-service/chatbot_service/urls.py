"""
URL configuration for chatbot_service project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/chat/', include('chat.urls')),
]
