import streamlit as st
import requests
from PIL import Image
import io

# URL de l'API FastAPI
API_URL = "http://localhost:8000/predict"

st.title("Image Classification with FastAPI")

# Uploader un fichier image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_file is not None:

    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)


    if st.button("Predict"):

        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            result = response.json()
            st.success(f"Prediction: {result['predicted_class']}")
            st.write("Prediction Details:", result['prediction'])
        else:
            st.error("Error in prediction: " + response.json().get('detail', 'Unknown error'))
