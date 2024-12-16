# store/recommendation/models/prepare_data.py
import pandas as pd
from django.contrib.auth.models import User
from store.models import UserInteraction, Rating, Product
from sklearn.model_selection import train_test_split

def fetch_UserInteraction():
    # Retrieve interactions from UserInteraction model
    interactions = UserInteraction.objects.all().values('user_id', 'product_id', 'action')  # Ensure field names match

    # Check if there is data retrieved
    if not interactions:
        print("No interactions found.")
        return pd.DataFrame()  # Return an empty DataFrame if no data found

    # Convert to DataFrame for easier manipulation
    interactions_df = pd.DataFrame(interactions)

    # Print the DataFrame columns to check the structure
    print("Columns in UserInteraction DataFrame:", interactions_df.columns)
    print("First few rows of UserInteraction DataFrame:\n", interactions_df.head())

    # Encode actions to numerical values (optional: useful for deep learning)
    action_mapping = {'view': 1, 'click': 2, 'add_to_cart': 3, 'purchase': 4}

    # Check if 'action' exists in the columns and map it
    if 'action' in interactions_df.columns:
        interactions_df['action'] = interactions_df['action'].map(action_mapping)
    else:
        print("Error: 'action' column is missing.")
        return pd.DataFrame()  # Return an empty DataFrame if no 'action' column

    return interactions_df



def fetch_ratings():
    # Retrieve ratings from the Rating model
    ratings = Rating.objects.all().values('user_id', 'product_id', 'rating')
    # Convert to DataFrame
    ratings_df = pd.DataFrame(ratings)
    return ratings_df

def merge_data(interactions_df, ratings_df):
    # Merge on user_id and product_id to combine implicit and explicit feedback
    merged_df = pd.merge(interactions_df, ratings_df, on=['user_id', 'product_id'], how='outer')

    # Fill NaNs for actions and ratings (optional handling)
    merged_df['action'].fillna(0, inplace=True)  # Use 0 if no interaction
    merged_df['rating'].fillna(0, inplace=True)  # Use 0 if no rating

    return merged_df

def split_data(merged_df):
    # Splitting data into train and test sets (e.g., 80-20 split)
    train, test = train_test_split(merged_df, test_size=0.2, random_state=42)
    return train, test

def prepare_data():
    # Step 1: Fetch interaction and ratings data
    interactions_df = fetch_UserInteraction()
    ratings_df = fetch_ratings()

    # Step 2: Merge data (optional for hybrid approaches)
    merged_df = merge_data(interactions_df, ratings_df)

    # Step 3: Split data into training and validation sets
    train, test = split_data(merged_df)

    # Save to CSV or directly use it in training
    train.to_csv('train_data.csv', index=False)
    test.to_csv('test_data.csv', index=False)

    print("Data preparation complete. Training and testing sets saved.")
