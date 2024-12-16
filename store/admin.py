from django.contrib import admin

from store.models import Category, Customer, Order, OrderItem, Product, ShippingAddress, Rating,UserInteraction

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(UserInteraction)
admin.site.register(Rating)