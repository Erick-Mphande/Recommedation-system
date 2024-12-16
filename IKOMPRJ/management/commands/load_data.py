import csv
from django.core.management.base import BaseCommand
#from .models import Product, Category, Customer, ProductView
from django.contrib.auth.models import User, Product, Category, Customer, ProductView

class Command(BaseCommand):
    help = 'Load data from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        file_path = options['file']
        if not file_path:
            self.stdout.write(self.style.ERROR("C:\Users\27728\Downloads\rs"))
            return
        
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    # Get or create category
                    category, _ = Category.objects.get_or_create(name=row['category'])

                    # Create product
                    product, created = Product.objects.get_or_create(
                        name=row['name'],
                        defaults={
                            'price': row['price'],
                            'description': row['description'],
                            'category': category,
                            'is_sale': row.get('is_sale', 'False').lower() == 'true',
                            'sale_price': row.get('sale_price', 0)
                        }
                    )

                    # Load user interactions for recommendations
                    # For simplicity, assuming CSV has columns like `user_email` and `viewed_product`
                    if 'user_email' in row and 'viewed_product' in row and row['viewed_product'].lower() == 'true':
                        user, _ = User.objects.get_or_create(username=row['user_email'], email=row['user_email'])
                        customer, _ = Customer.objects.get_or_create(user=user, email=user.email)
                        ProductView.objects.create(customer=customer, product=product)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created product: {product.name}"))

            self.stdout.write(self.style.SUCCESS("Data loading completed successfully."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))