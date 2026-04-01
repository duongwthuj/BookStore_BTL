"""
URL configuration for chat app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('search-book/', views.search_book, name='search-book'),
    path('order-status/<str:order_id>/', views.order_status, name='order-status'),
    path('health/', views.health, name='health'),
]
