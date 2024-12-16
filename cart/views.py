from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Order, OrderItem, Product
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()  # Ensure this function exists in your cart class
    return render(request, "cart_summary.html", {"cart_products": cart_products})

@require_POST
def cart_add(request):
    print("Request POST data:", request.POST)  # Log the incoming POST data
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        try:
            product_id = int(request.POST.get('product_id'))
            product_qty = int(request.POST.get('product_qty'))
            product = get_object_or_404(Product, id=product_id)
            cart.add(product=product, quantity=product_qty)
            cart_quantity = len(cart)
            cart_total_price = cart.get_total_price()  # Get cart total price
            response = JsonResponse({'qty': cart_quantity, 'total_price': cart_total_price})
            return response
        except (Product.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Invalid product ID or quantity'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_POST
def cart_delete(request):
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    
    if not product_id:
        return JsonResponse({'error': 'Invalid product ID'}, status=400)

    try:
        product_id = int(product_id)
        product = get_object_or_404(Product, id=product_id)
    except (ValueError, Product.DoesNotExist):
        return JsonResponse({'error': 'Invalid product ID'}, status=400)

    cart.remove(product)
    cart_quantity = len(cart)
    cart_total_price = cart.get_total_price()
    
    return JsonResponse({'qty': cart_quantity, 'total_price': cart_total_price})


@require_POST
def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'update':
        try:
            product_id = int(request.POST.get('product_id'))
            product_qty = int(request.POST.get('product_qty'))
            product = get_object_or_404(Product, id=product_id)
            cart.update(product=product, quantity=product_qty)
            cart_quantity = len(cart)
            cart_total_price = cart.get_total_price()  # Get cart total price
            response = JsonResponse({'qty': cart_quantity, 'total_price': cart_total_price})
            return response
        except (Product.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Invalid product ID or quantity'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

