import streamlit as st
import requests
from PIL import Image
import io

API_URL = "http://localhost:8000/predict"

st.title("Image Classification")

uploaded_file = st.file_uploader("Choose an image")

if uploaded_file is not None:
    st.write(f"Uploaded file type: {uploaded_file.type}")

    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    if st.button("Predict"):

        response = requests.post(API_URL, files={"file": ("image.png", img_bytes, "image/png")})

        if response.status_code == 200:
            prediction = response.json().get("prediction")
            confidence = response.json().get("confidence")
            st.success(f"Prediction: {prediction}")
            if confidence:
                st.write(f"Confidence: {confidence:.2f}%")
        else:
            st.error(f"Failed to get prediction. Status code: {response.status_code}")
            st.write(response.text)
