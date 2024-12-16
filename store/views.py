from argparse import Action
from datetime import timezone
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F



from cart import models
from cart.cart import Cart
from .models import Category, Customer, Order, Product, Rating, ShippingAddress, UserInteraction
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import RatingForm, SignUpForm, UserProfileForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View 
from django.urls import reverse_lazy
from uuid import uuid4
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count, Q
from django.db.models import Avg
from django.db.models import Count
from collections import defaultdict
import numpy as np
from scipy.spatial.distance import cosine
from .models import Product, Rating, ViewingHistory, OrderItem
# ikom/views.py

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import tensorflow as tf

from store import recommendations  # or `from tensorflow.keras.models import load_model`
# Or, if using a scikit-learn model:
# import joblib

# Load the model (assuming TensorFlow/Keras here)
model_path = os.path.join(settings.BASE_DIR, r'C:\Users\27728\Desktop\IKOMPRJ\store\recommendations\models\ncf_model.h5')
model = tf.keras.models.load_model(model_path)
# Or, if using Scikit-learn:
# model_path = os.path.join(settings.BASE_DIR, 'ikom/models/your_saved_model.pkl')
# model = joblib.load(model_path)

@login_required
@csrf_exempt
def clear_cart(request):
    if request.method == "POST":
        try:
            cart = request.user.cart  # Assuming the user has a `cart` attribute or a `get_cart()` method
            cart_items = cart.cartitem_set.all()  # Adjust if your cart items are accessed differently
            
            # Update product quantities (if your cart logic deducts from available stock)
            for item in cart_items:
                product = item.product
                product.stock += item.quantity
                product.save()

            # Clear the cart
            cart.cartitem_set.all().delete()

            return JsonResponse({"success": True, "message": "Cart cleared successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})


def product_list(request):
    products = Product.objects.annotate(avg_rating=Avg('rating__rating')).all()
    popular_products = Product.objects.order_by('-view_count')[:5]
    context = {
        'products': products,
        'popular_products': popular_products,
    }
    return render(request, 'home.html', context)


# Helper function to generate transaction ID
def generate_transaction_id():
    return str(uuid4())

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def about(request):
    return render(request, 'about.html', {})

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    recommendations = Product.objects.filter(category=product.category).exclude(id=product.id)[:5]

    # Calculate the average rating
    avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    reviews = product.reviews.all()

    # Render the product details and recommendations to the template
    return render(request, 'product_detail.html', {
        'product': product,
        'recommendations': recommendations,
        'avg_rating': round(avg_rating, 2),
        'reviews': reviews,
    })



# Category and Product Views
def category_summary(request):
    categories = Category.objects.all()  # Retrieve all categories from the database
    return render(request, 'category_summary.html', {'categories': categories})

def category_detail(request, category_id):
    try:
        category = Category.objects.get(id=category_id)  # Fetch the category by ID
        products = Product.objects.filter(category=category)  # Get all products in that category
        return render(request, 'category_detail.html', {'category': category, 'products': products})
    except Category.DoesNotExist:
        messages.error(request, "That category does not exist.")
        return redirect('home')  # Redirect to the home page if the category doesn't exist

# View to display products based on category name (slug or formatted name)
def category(request, foo):
    foo = foo.replace('-', ' ')  # Replace hyphens with spaces in the category name (if slug format)

    try:
        category = Category.objects.get(name__iexact=foo)  # Fetch category by name, case insensitive
        products = Product.objects.filter(category=category)  # Get products belonging to this category
        return render(request, 'category.html', {'category': category, 'products': products})
    except Category.DoesNotExist:
        messages.error(request, "That Category does not exist.")
        return redirect('home')


def product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # Store viewing history if the user is authenticated
    if request.user.is_authenticated:
        # Log user interaction: viewing a product
        UserInteraction.objects.create(
            user=request.user,
            product=product,
            action='view',
            #timestamp=timezone.now()  # Correct usage of timezone.now()
        )

    # Fetch recommendations (for example, based on a model or logic)
    recommendations = get_product_recommendations(product)

    return render(request, 'product_detail.html', {
        'product': product,
        'recommendations': recommendations,  # Pass recommendations to the template
    })


# User Authentication Views
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "You have been logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have registered successfully!")
            return redirect('login')
        else:
            messages.error(request, "Error occurred during registration. Please check your inputs.")
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(View):
    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, 'Update_profile.html', {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_update')
        return render(request, 'Update_profile.html', {'form': form})


# Checkout and Order Processing
def checkout(request):
    items = request.session.get('cart', {})
    order_items = []
    total = 0

    for item_id, quantity in items.items():
        product = Product.objects.get(id=item_id)
        quantity = quantity.get('quantity', 0) if isinstance(quantity, dict) else quantity
        total += product.price * int(quantity)
        order_items.append({'product': product, 'quantity': quantity})

    context = {'items': order_items, 'total': total, 'user': request.user, 'digital_order': False}
    return render(request, 'checkout.html', context)


# Guest-friendly order processing
def process_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = data['form']['total']
            shipping_info = data.get('shipping', {})
            cart = request.session.get('cart', {})

            if not cart:
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            order = Order.objects.get_or_create(user=request.user if request.user.is_authenticated else None, complete=False)[0]
            total_amount = sum(Product.objects.get(id=item_id).price * int(quantity) for item_id, quantity in cart.items())
            
            if float(total) != total_amount:
                return JsonResponse({'error': 'Total price mismatch'}, status=400)

            if shipping_info:
                ShippingAddress.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    order=order,
                    address=shipping_info['address'],
                    city=shipping_info['city'],
                    state=shipping_info['state'],
                    zipcode=shipping_info['zipcode'],
                    country=shipping_info['country']
                )

            order.transaction_id = generate_transaction_id()
            order.complete = True
            order.save()
            request.session['cart'] = {}

            return JsonResponse('Order processed successfully', safe=False)

        except KeyError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@require_POST
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating_value = int(request.POST.get('rating', 0))

    if 1 <= rating_value <= 5:
        # Save or update the rating
        Rating.objects.update_or_create(user=request.user, product=product, defaults={'rating': rating_value})
        
        # Log the rating interaction
        UserInteraction.objects.create(user=request.user, product=product, action='rate', timestamp=timezone.now())

        return JsonResponse({'status': 'success', 'message': 'Rating submitted successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid rating value.'})

def product_rating(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    ratings = Rating.objects.filter(product=product)
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    user_rating = None
    
    # Check if the user is authenticated before accessing their rating
    if request.user.is_authenticated:
        user_rating = ratings.filter(user=request.user).first()
    else:
        # Redirect to login if the user is not authenticated
        return redirect('login')

    star_range = [1, 2, 3, 4, 5]

    if request.method == 'POST':
        # Ensure the user is authenticated before saving a rating
        if request.user.is_authenticated:
            rating_value = request.POST.get('rating')
            if rating_value:
                Rating.objects.update_or_create(
                    product=product,
                    user=request.user,
                    defaults={'rating': rating_value}
                )
                return redirect('product_rating', product_id=product.id)
        else:
            return redirect('login')

    context = {
        'product': product,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'user_rating': user_rating,
        'star_range': star_range,
    }

    return render(request, 'product_rating.html', context)



@login_required
def order(request):
    order, created = Order.objects.get_or_create(user=request.user, complete=False)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = data['form']['total']
            shipping_info = data.get('shipping', {})

            # Handle guest users
            if not request.user.is_authenticated:
                order.guest = True

           
                ShippingAddress.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    order=order,
                    address=shipping_info['address'],
                    city=shipping_info['city'],
                    state=shipping_info['state'],
                    zipcode=shipping_info['zipcode'],
                    country=shipping_info['country']
                )

            order.transaction_id = generate_transaction_id()
            order.complete = True
            order.save()

            # Clear the cart after order is completed
            request.session['cart'] = {}

            return JsonResponse('Order processed successfully', safe=False)
        except KeyError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def generate_transaction_id():
    return str(uuid4())

# Existing functions for handling products, categories, and user management ...

def checkout(request):
    items = request.session.get('cart', {})
    order_items = []
    total = 0

    for item_id, quantity in items.items():
        product = Product.objects.get(id=item_id)
        if isinstance(quantity, dict):
            quantity = quantity.get('quantity', 0)
        total += product.price * int(quantity)

        order_items.append({'product': product, 'quantity': quantity})

    context = {
        'items': order_items,
        'total': total,
        'user': request.user,
        'digital_order': False,
    }
    
    return render(request, 'checkout.html', context)

# Guest-friendly order processing
def process_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        total = data['form']['total']
        shipping_info = data.get('shipping', {})
        cart = request.session.get('cart', {})

        if not cart:
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        # If the user is authenticated, use their existing order or create a new one
        if request.user.is_authenticated:
            order, created = Order.objects.get_or_create(user=request.user, complete=False)
        else:
            # Create a temporary order for guest users
            order = Order.objects.create(complete=False, guest=True)
        
        # Add products to the order from the session cart
        total_amount = 0
        for item_id, quantity in cart.items():
            product = Product.objects.get(id=item_id)
            if isinstance(quantity, dict):
                quantity = quantity.get('quantity', 0)
            total_amount += product.price * int(quantity)

        if float(total) != total_amount:
            return JsonResponse({'error': 'Total price mismatch'}, status=400)

        # Handle shipping information
        if shipping_info:
            ShippingAddress.objects.create(
                user=request.user if request.user.is_authenticated else None,
                order=order,
                address=shipping_info['address'],
                city=shipping_info['city'],
                state=shipping_info['state'],
                zipcode=shipping_info['zipcode'],
                country=shipping_info['country']
            )

        # Complete the order
        order.transaction_id = generate_transaction_id()
        order.complete = True
        order.save()

        # Log the purchase interaction
        for item_id, quantity in cart.items():
            product = Product.objects.get(id=item_id)
            UserInteraction.objects.create(user=request.user, product=product, action='purchase', timestamp=timezone.now())

        # Clear the cart after order is completed
        request.session['cart'] = {}

        return JsonResponse('Order processed successfully', safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def popular_products(request):
    # Get popular products based on view count
    popular_by_views = Product.objects.order_by('-view_count')[:5]

    # Get popular products based on purchases
    popular_by_purchases = Product.objects.annotate(
        purchase_count=Count('userinteraction', filter=models.Q(userinteraction__action='purchase'))
    ).order_by('-purchase_count')[:5]

    return render(request, 'popular_products.html', {
        'popular_by_views': popular_by_views,
        'popular_by_purchases': popular_by_purchases,
    })

from .recommendations import get_product_recommendations
# View Product and Track Viewing History
def view_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # Store viewing history if the user is authenticated
    if request.user.is_authenticated:
        # Log user interaction: viewing a product
        UserInteraction.objects.create(
            user=request.user,
            product=product,
            action='view',
            #timestamp=timezone.now()  # Correct usage of timezone.now()
        )

    # Fetch recommendations (for example, based on a model or logic)
    recommendations = get_product_recommendations(product)

    return render(request, 'product_detail.html', {
        'product': product,
        'recommendations': recommendations,  # Pass recommendations to the template
    })

# Helper: Retrieve average rating for a product
def product_rating_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    avg_rating = Rating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
    user_rating = Rating.objects.filter(product=product, user=request.user).first() if request.user.is_authenticated else None

    return render(request, 'product_rating.html', {
        'product': product,
        'avg_rating': avg_rating,
        'user_rating': user_rating,
        'star_range': range(1, 6),  # For displaying 1-5 star ratings
    })





# Load the trained model (ensure the model path is correct)
from django.shortcuts import render
from .models import Product
import numpy as np
import tensorflow as tf  # Use TensorFlow to load the .h5 model
from .encoder import user_encoder, product_encoder
from sklearn.preprocessing import LabelEncoder



# Load the trained model (ensure the model path is correct)
model_path = r'C:/Users/27728/Desktop/IKOMPRJ/store/recommendations/models/ncf_model.h5'
model = tf.keras.models.load_model(model_path)

import numpy as np

user_encoder = LabelEncoder()
product_encoder = LabelEncoder()

# Sample data preparation for demonstration - fit the encoders with actual user and product data beforehand
# user_encoder.fit(user_ids) 
# product_encoder.fit(product_ids) 

def get_recommendations(user_data, model, user_encoder, product_encoder):
    """
    Generate product recommendations based on user data.
    
    Parameters:
    - user_data (tuple): Tuple containing user ID and product ID for predictions.
    - model: The loaded machine learning model.
    - user_encoder, product_encoder: Encoders for user and product IDs.
    
    Returns:
    - recommendations (list): List of recommended product IDs.
    """
    try:
        # Fit the encoder if not already done (this is just an example; avoid fitting repeatedly in production)
        user_encoder.fit([user_data[0]])  # Fit user_encoder on the user_data
        product_encoder.fit([user_data[1]])  # Fit product_encoder on the product_data
        
        # Separate user and product IDs
        user_id, product_id = user_data
        user_input = np.array([user_encoder.transform([user_id])], dtype=np.int32)
        product_input = np.array([product_encoder.transform([product_id])], dtype=np.int32)
    except ValueError as e:
        print(f"Error preparing inputs: {e}")
        return []

    # Predict using the model
    predictions = model.predict([user_input, product_input])

    # Get the top 5 recommended items
    recommended_items = predictions.flatten().argsort()[::-1][:5]
    return recommended_items



def recommended_products_view(request):
    # Implement your logic for fetching recommendations here
    recommended_products = Product.objects.all()  # Example, replace with your recommendation logic
    return render(request, 'search_results.html', {'recommended_products': recommended_products})

def search_results(request):
    query = request.GET.get('q')
    results = []
    personalized_recommendations = []

    if query:
        # Retrieve matching products
        results = Product.objects.filter(name__icontains=query) | Product.objects.filter(description__icontains=query)

        if results.exists():
            # Example of fetching user-specific data (replace with actual user and product IDs from session or context)
            user_id = request.user.id
            product_id = results.first().id  # Only set the product_id if there are matching results

            if user_id and product_id:
                # Pass user_id and product_id as a tuple to get_recommendations
                personalized_recommendations = get_recommendations((user_id, product_id), model, user_encoder, product_encoder)

    # Fetch all products for the filter (if needed)
    all_products = Product.objects.all()

    return render(request, 'search_results.html', {
        'results': results,
     # Pass all products here
        'product': product,
        'recommendations': recommendations,
    })





# Functions to encode user and product data once
from sklearn.preprocessing import LabelEncoder

# Global label encoders for users and products (could also be done in the model setup)
user_encoder = LabelEncoder()
product_encoder = LabelEncoder()

def encode_users(user_data):
    """
    Encodes user identifiers (e.g., usernames or IDs) into numeric format.

    Parameters:
    - user_data (list or Series): List or Pandas Series of user identifiers (usernames or user IDs).

    Returns:
    - encoded_users (np.array): Array of encoded user identifiers.
    """
    # Fit the encoder only once on the unique user data
    return user_encoder.fit_transform(user_data)


def encode_products(products):
    """
    Encodes a list of product names or IDs into numerical values.

    Args:
        products (list): List of product names or IDs.

    Returns:
        np.array: Array of numerical values representing the products.
    """
    # Fit the encoder only once on the unique product data
    return product_encoder.fit_transform(products)

# When loading user data and product data
all_users = User.objects.values_list('id', flat=True)  # Or however you fetch users
all_products = Product.objects.values_list('id', flat=True)  # Or however you fetch products

# Fit the encoders on the complete data once
encode_users(all_users)
encode_products(all_products)
