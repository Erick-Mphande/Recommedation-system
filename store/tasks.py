# yourapp/tasks.py
from celery import shared_task
from .models import Product

@shared_task
def update_popular_products():
    # Task logic to update popular product metrics
    popular_products = Product.objects.all()  # Example query
    for product in popular_products:
        product.update_metrics()  # Hypothetical method to update metrics
        product.save()
