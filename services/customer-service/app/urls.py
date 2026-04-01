from django.urls import path

from . import views

urlpatterns = [
    path('customers/', views.customer_list, name='customer-list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer-detail'),
    path('customers/by-user/<int:user_id>/', views.customer_by_user, name='customer-by-user'),
]
