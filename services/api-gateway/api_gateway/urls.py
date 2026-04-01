"""
URL configuration for api_gateway project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('app.urls')),
]
