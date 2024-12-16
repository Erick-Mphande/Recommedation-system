# Import necessary libraries
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Sample function to encode user IDs or usernames
def user_encoder(user_data):
    """
    Encodes user identifiers (e.g., usernames or IDs) into numeric format.

    Parameters:
    - user_data (list or Series): List or Pandas Series of user identifiers (usernames or user IDs).

    Returns:
    - encoded_users (Series): Pandas Series of encoded user identifiers.
    - encoder (LabelEncoder): Fitted encoder object, to decode or transform other data later if needed.
    """
    # Initialize the LabelEncoder
    encoder = LabelEncoder()
    
    # Fit and transform the user data
    encoded_users = encoder.fit_transform(user_data)
    
    
    return pd.Series(encoded_users), encoder

def product_encoder(products):
    """
    Encodes a list of product names or IDs into numerical values.

    Args:
        products (list): List of product names or IDs.

    Returns:
        tuple: (encoded_products, encoder), where:
            - encoded_products is a list of numerical values representing the products.
            - encoder is the fitted LabelEncoder instance, which can be used for decoding.
    """
    encoder = LabelEncoder()
    encoded_products = encoder.fit_transform(products)
    return encoded_products, encoder