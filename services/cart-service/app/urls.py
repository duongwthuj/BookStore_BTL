from django.urls import path
from . import views

urlpatterns = [
    # New simplified endpoints (get user from JWT token via X-User-Id header)
    path('cart/', views.get_my_cart, name='my-cart'),
    path('cart/items/', views.add_my_item, name='add-my-item'),
    path('cart/items/<int:item_id>/', views.my_item_detail, name='my-item-detail'),
    path('cart/clear/', views.clear_my_cart, name='clear-my-cart'),

    # Legacy endpoints with customer_id in URL (for internal service communication)
    path('carts/', views.create_cart, name='create-cart'),
    path('carts/<int:customer_id>/', views.get_cart, name='get-cart'),
    path('carts/<int:customer_id>/items/', views.add_item, name='add-item'),
    path('carts/<int:customer_id>/items/<int:item_id>/', views.item_detail, name='item-detail'),
    path('carts/<int:customer_id>/clear/', views.clear_cart, name='clear-cart'),
]
