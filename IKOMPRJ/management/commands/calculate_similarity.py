# management/commands/calculate_similarity.py
import pandas as pd
from django.core.management.base import BaseCommand
from store.models import Product, UserInteraction, ProductSimilarity
from sklearn.metrics.pairwise import cosine_similarity
from django.db import transaction

class Command(BaseCommand):
    help = 'Calculate item-item similarity for collaborative filtering'

    def handle(self, *args, **kwargs):
        # Load user interactions data
        interactions = UserInteraction.objects.all().values('user_id', 'product_id')
        df = pd.DataFrame(interactions)

        # Create a user-product interaction matrix
        interaction_matrix = pd.crosstab(df['user_id'], df['product_id'])

        # Compute cosine similarity between products
        similarity_matrix = cosine_similarity(interaction_matrix.T)

        # Convert to DataFrame for easier manipulation
        similarity_df = pd.DataFrame(
            similarity_matrix, index=interaction_matrix.columns, columns=interaction_matrix.columns
        )

        # Clear existing similarity data and start a transaction
        with transaction.atomic():
            ProductSimilarity.objects.all().delete()
            
            # Insert top 5 similar products for each product
            for product_id in similarity_df.index:
                similar_products = similarity_df[product_id].nlargest(6).index  # Top 5 similar products
                for similar_product_id in similar_products:
                    if product_id != similar_product_id:
                        ProductSimilarity.objects.create(
                            product_id=product_id,
                            similar_product_id=similar_product_id,
                            similarity_score=similarity_df.at[product_id, similar_product_id]
                        )

        self.stdout.write(self.style.SUCCESS("Product similarity calculation completed."))
