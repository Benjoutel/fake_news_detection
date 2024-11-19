
from fastapi import FastAPI, File, UploadFile, HTTPException
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import one_hot
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from pydantic import BaseModel
from transformers import pipeline
from PIL import Image
#from call_openai import openai_call_for_fakenews_check
import numpy as np
import tempfile
import os
import re
import uvicorn

app = FastAPI()

@app.get('/')
def index():
    return {'ok': True}


# model image
model_image_path = os.path.join("model.keras")
model_image = load_model(model_image_path)


########################## PREDICT ON IMAGE
def load_and_preprocess_image(image_path):
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = preprocess_input(image)
    image = np.expand_dims(image, axis=0)
    return image

from transformers import pipeline
from PIL import Image

classifier = pipeline("image-classification", model="NYUAD-ComNets/NYUAD_AI-generated_images_detector")

@app.post("/predict_image")
async def predict(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG or PNG image.")

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        image = image = Image.open(tmp_path)

        prediction = classifier(image)
        label = prediction[0]['label']
        confidence = prediction[0]['score']

        os.remove(tmp_path)

        return {
            "prediction": label,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)



########################## PREDICT ON TEXT

print("Start loading text model...")
# model image
model_text_path = os.path.join("my_model.keras")
model_text = load_model(model_text_path)


# Stopwords and text processing
stop_words = stopwords.words('english')
print("Stopwords loaded successfully.")
max_length = 42  # Based on training configuration

# Text cleaning
text_cleaning = "\b0\S*|\b[^A-Za-z0-9]+"

def preprocess_filter(text, stem=False):
  text = re.sub(text_cleaning, " ",str(text.lower()).strip())
  tokens = []
  for token in text.split():
    if token not in stop_words:
      if stem:
        stemmer = SnowballStemmer(language='english')
        token = stemmer.stem(token)
      tokens.append(token)
  return " ".join(tokens)

# Word embedding with pre padding
def one_hot_encoded(text,vocab_size=5000,max_length = 40):
    hot_encoded = one_hot(text,vocab_size)
    return hot_encoded


# word embedding pipeline
def word_embedding(text):
    preprocessed_text=preprocess_filter(text)
    return one_hot_encoded(preprocessed_text)

# ensure the TextPayload class is recognized
class TextPayload(BaseModel):
    text: str

# Text prediction endpoint
@app.post("/predict_text")
async def predict_text(payload: TextPayload):
    try:
        preprocessed_text = preprocess_filter(payload.text)
        print("preprocessing text...")
        embedded_text = word_embedding(preprocessed_text)
        print("embbeding text...")
        padded_text = pad_sequences([embedded_text], maxlen=max_length, padding='pre')
        print("last step before prediction")

        prediction = model_text.predict(padded_text)
        threshold = 0.8
        label = 1 if prediction[0][0] > threshold else 0
        local_result = "Fake News" if label == 1 else "Real News"

        # Retour des résultats combinés
        return {
            "text": payload.text,
            "local_prediction": local_result,
            "local_confidence": float(prediction[0][0])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))