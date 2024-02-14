from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name = 'cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name = 'add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item__id>/', views.remove_cart, name = 'remove_cart'),
    path('remove__cart_item/<int:product_id>/<int:cart_item__id>/', views.remove__cart_item, name = 'remove__cart_item'),
    
]