
import tensorflow as tensorflow
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
from tensorflow.keras.models import load_model

model_path ="/Users/najiaraji/code/AurelienCardon/fake_news_detection/model.keras"
model = load_model(model_path)

def load_and_preprocess_image(image_path):

    image = load_img(image_path, target_size=(32,32))
    image = img_to_array(image)
    image = preprocess_input(image)
    image = np.expand_dims(image, axis=0)

    return image

def predict(image):

    model = load_model(model_path)

    prediction = model.predict(image)

    return prediction
