"""
URL configuration for recommender_service project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),  # Prefix with /api/ so full path is /api/recommend/
]
