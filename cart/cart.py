from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart and quantity > 0:
            self.cart[product_id]['quantity'] = quantity
            self.save()
        elif quantity <= 0:
            self.remove(product)

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart_products = []
        for product in products:
            cart_products.append({
                'product': product,
                'quantity': self.cart[str(product.id)]['quantity'],
                'price': float(self.cart[str(product.id)]['price']),
                'total_price': float(self.cart[str(product.id)]['price']) * self.cart[str(product.id)]['quantity'],
            })
        return cart_products
