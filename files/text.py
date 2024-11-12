
from importlib.resources import read_text
import tensorflow as tensorflow
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np
from tensorflow.keras.models import load_model
import fitz  # PyMuPDF


model_path ="/Users/najiaraji/code/AurelienCardon/fake_news_detection/notebooks/model.text/my_model.keras"
model = load_model(model_path)

pdf_path="/Users/najiaraji/Downloads/text1.pdf"

def read_pdf_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()

    pdf_document.close()

    return text

read_pdf_text(pdf_path)

def predict(text):

    model = load_model(model_path)

    prediction = model.predict(text)

    return prediction
