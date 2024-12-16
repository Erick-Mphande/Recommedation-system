import pandas as pd
import numpy as np
import tensorflow as tf
from keras import layers, models
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Load and preprocess data
def load_data():
    # Load train data (you may adjust the path if necessary)
    train_data = pd.read_csv('train_data.csv')
    test_data = pd.read_csv('test_data.csv')
    
    return train_data, test_data

# Preprocessing for Neural Collaborative Filtering
def preprocess_data(train_data, test_data):
    # Encode user and product IDs using LabelEncoder
    user_encoder = LabelEncoder()
    product_encoder = LabelEncoder()

    train_data['user'] = user_encoder.fit_transform(train_data['user_id'])
    train_data['product'] = product_encoder.fit_transform(train_data['product_id'])
    
    test_data['user'] = user_encoder.transform(test_data['user_id'])
    test_data['product'] = product_encoder.transform(test_data['product_id'])

    return train_data, test_data, user_encoder, product_encoder

# Build the Neural Collaborative Filtering Model
def build_model(num_users, num_products, embedding_dim=50):
    # User and Product embeddings
    user_input = layers.Input(shape=(1,), name='user')
    product_input = layers.Input(shape=(1,), name='product')
    
    user_embedding = layers.Embedding(input_dim=num_users, output_dim=embedding_dim)(user_input)
    product_embedding = layers.Embedding(input_dim=num_products, output_dim=embedding_dim)(product_input)
    
    # Flatten the embeddings
    user_vec = layers.Flatten()(user_embedding)
    product_vec = layers.Flatten()(product_embedding)
    
    # Concatenate the user and product embeddings
    concat = layers.Concatenate()([user_vec, product_vec])
    
    # Fully connected layers
    dense_1 = layers.Dense(256, activation='relu')(concat)
    dense_2 = layers.Dense(128, activation='relu')(dense_1)
    output = layers.Dense(1, activation='linear')(dense_2)  # Regression task (rating prediction)

    model = models.Model(inputs=[user_input, product_input], outputs=output)
    model.compile(optimizer='adam', loss='mean_squared_error')

    return model

# Train the Model
def train_model(model, train_data):
    # Prepare training data
    user_input = train_data['user']
    product_input = train_data['product']
    ratings = train_data['rating']  # Assuming rating as the target variable
    
    # Train the model
    model.fit([user_input, product_input], ratings, epochs=10, batch_size=64, validation_split=0.2)

# Save the model
def save_model(model):
    # Specify the correct path where you want to save the model
    model_save_path = r'C:/Users/27728/Desktop/IKOMPRJ/store/recommendations/models/ncf_model.h5'
    
    # Save the model to the specified path
    model.save(model_save_path)

# Load the trained model
def load_trained_model():
    # Specify the correct path where the model is saved
    model_path = r'C:/Users/27728/Desktop/IKOMPRJ/store/recommendations/models/ncf_model.h5'
    
    # Load the model from the specified path
    return models.load_model(model_path)

# Prediction function
def predict(user_id, product_id, model, user_encoder, product_encoder):
    user_input = np.array([user_encoder.transform([user_id])])
    product_input = np.array([product_encoder.transform([product_id])])
    
    prediction = model.predict([user_input, product_input])
    return prediction[0][0]  # Return the predicted rating
