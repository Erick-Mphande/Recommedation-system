import os
from tensorflow.keras.models import load_model
from .config import MODEL_PATH

def load_recommendation_model():
    if os.path.exists(MODEL_PATH):
        return load_model(MODEL_PATH)
    else:
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
