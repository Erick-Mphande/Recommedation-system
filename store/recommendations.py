# store/recommendations.py

from .models import Product, UserInteraction

def get_product_recommendations(product):
    # This is a simple example where we fetch products that have been viewed by users who viewed the same product
    interactions = UserInteraction.objects.filter(product=product, action='view')
    
    recommended_products = set()  # To store unique recommendations
    
    # Loop through all interactions and get other products that the same users interacted with
    for interaction in interactions:
        related_interactions = UserInteraction.objects.filter(user=interaction.user).exclude(product=product)
        for related_interaction in related_interactions:
            recommended_products.add(related_interaction.product)
    
    # Limit the number of recommendations to avoid overwhelming the user
    recommended_products = list(recommended_products)[:5]  # Example: Return only top 5 recommended products
    return recommended_products

