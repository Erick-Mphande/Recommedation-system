import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from store.models import UserProductInteraction

def load_user_item_matrix():
    # Retrieve user-product interaction data
    data = list(UserProductInteraction.objects.values('user_id', 'product_id', 'rating'))
    df = pd.DataFrame(data)
    user_item_matrix = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)
    return user_item_matrix

def collaborative_recommendations(user_id, num_recommendations=10):
    user_item_matrix = load_user_item_matrix()
    svd = TruncatedSVD(n_components=20)
    decomposed_matrix = svd.fit_transform(user_item_matrix)
    cosine_sim = cosine_similarity(decomposed_matrix)
    
    user_index = user_item_matrix.index.get_loc(user_id)
    similar_users = list(enumerate(cosine_sim[user_index]))
    similar_users = sorted(similar_users, key=lambda x: x[1], reverse=True)

    recommendations = []
    for i, _ in similar_users[1:num_recommendations + 1]:  # Get top N similar users
        recommendations.extend(user_item_matrix.columns[user_item_matrix.iloc[i] > 0].tolist())
    return list(set(recommendations))[:num_recommendations]  # Return unique recommendations
