"""
URL configuration for chat app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Chat
    path('', views.chat, name='chat'),
    path('search-book/', views.search_book, name='search-book'),
    path('order-status/<str:order_id>/', views.order_status, name='order-status'),

    # Sessions
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/<str:session_id>/', views.session_detail, name='session-detail'),
    path('history/<str:session_id>/', views.session_history, name='session-history'),

    # Documents (Knowledge Base)
    path('documents/', views.documents, name='documents'),
    path('documents/<str:doc_id>/', views.document_detail, name='document-detail'),

    # Admin / Sync
    path('sync-books/', views.sync_books, name='sync-books'),
    path('rag-stats/', views.rag_stats, name='rag-stats'),

    # Health
    path('health/', views.health, name='health'),
]
