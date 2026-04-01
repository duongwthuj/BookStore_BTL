"""
URL configuration for comment_rate_service project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
]
