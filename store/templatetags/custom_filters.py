from django import template
from store.models import Product

register = template.Library()

@register.filter
def get_product_by_id(products, product_id):
    """Returns the product with the given ID from the list of products."""
    return products.get(id=product_id) if products else None
