from django.urls import path, reverse_lazy
from cart.views import cart_add, cart_summary, cart_delete  # Ensure these views are defined
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordChangeForm  # Import the custom form if you've defined it

urlpatterns = [
    # Home and About
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('recommendations/', views.recommended_products_view, name='recommendations'),

    # User Authentication
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

    # Product and Category Views
    path('product/<int:pk>/', views.product, name='product'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('category/<str:foo>/', views.category, name='category'),
    path('categories/', views.category_summary, name='category_summary'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),

    # Cart Actions
    path('cart/add/', cart_add, name='cart_add'),
    path('cart/', cart_summary, name='cart_summary'),
    path('cart/delete/', cart_delete, name='cart_delete'),  # Ensure this view exists

    # Profile Update
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),

    # Password Change
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             form_class=CustomPasswordChangeForm,
             success_url=reverse_lazy('password_change_done'),
             template_name='password_change.html'
         ),
         name='password_change'),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
         name='password_change_done'),
    
    # Search Functionality
    path('search/', views.search_results, name='search'),
    path('rate/<int:product_id>/', views.rate_product, name='rate_product'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    # Checkout and Order Processing
    path('checkout/', views.checkout, name='checkout'),
    path('process_order/', views.order, name='process_order'),  # Remove duplicate path
    path('product/<int:product_id>/rate/', views.product_rating, name='product_rating'),
    path('product/<int:product_id>/rate/', views.product_rating, name='product_rating'),
    path('product/<int:product_id>/rate/', views.product_rating, name='product_rating'),
    path('view_product/<int:pk>/', views.view_product, name='view_product'),
    path('view_product/<int:product_id>/', views.view_product, name='view_product'),
    path('product/<int:pk>/', views.product, name='product')


  
]
