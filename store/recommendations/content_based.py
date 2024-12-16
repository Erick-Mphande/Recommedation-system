from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from store.models import Product

def load_product_data():
    products = list(Product.objects.values('id', 'description'))
    return pd.DataFrame(products)

def content_based_recommendations(product_id, num_recommendations=10):
    product_data = load_product_data()
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(product_data['description'])
    
    cosine_sim = cosine_similarity(tfidf_matrix)
    product_idx = product_data[product_data['id'] == product_id].index[0]
    similar_indices = cosine_sim[product_idx].argsort()[-num_recommendations-1:-1][::-1]
    return product_data['id'].iloc[similar_indices].tolist()
