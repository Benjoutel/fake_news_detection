from fastapi import FastAPI, File, UploadFile, HTTPException
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
import numpy as np
import uvicorn
import tempfile
import os

app = FastAPI()

@app.get('/')
def index():
    return {'ok': True}

# model
model_path = os.path.join("model.keras")
model = load_model(model_path)


def load_and_preprocess_image(image_path):
    image = load_img(image_path, target_size=(224, 224))
    image = img_to_array(image)
    image = preprocess_input(image)
    image = np.expand_dims(image, axis=0)
    return image

from transformers import pipeline
from PIL import Image

classifier = pipeline("image-classification", model="NYUAD-ComNets/NYUAD_AI-generated_images_detector")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a valid image.")

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
