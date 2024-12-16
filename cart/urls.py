from django.urls import path
from . import views

urlpatterns = [
  path('', views.cart_summary, name="cart_summary"),
 
  path('cart/', views.cart_add, name="cart_add"),
  path('delete/', views.cart_delete, name="cart_delete"),
  path('cart/update/', views.cart_update, name="cart_update"),
  path('add/<int:product_id>/', views.cart_add, name='cart_add'), 
  


] 