import os
from tensorflow.keras.models import load_model

# Update this path to match where your model file is located in the project structure
model_path = os.path.join(settings.BASE_DIR, r'C:\Users\27728\Desktop\IKOMPRJ\store\recommendations\models\ncf_model.h5')
model = tf.keras.models.load_model(model_path)

# Load the model
try:
    MODEL = load_model(model_path)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load model: {e}")
