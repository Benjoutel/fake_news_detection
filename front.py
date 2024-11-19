import streamlit as st
import requests
from PIL import Image
from bs4 import BeautifulSoup
import io
from io import BytesIO
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # need to specify access url to pytesseract for streamlit cloud
import numpy as np
from googlesearch import search
import os
from call_openai import openai_call_for_fakenews_check

# URL to use for testing the deployed container
API_URL = "https://fake-news-image-863060191445.europe-west1.run.app/predict_image"

API_URL_TEXT = "https://fake-news-image-863060191445.europe-west1.run.app/predict_text"

# URL to use for local testing image
#API_URL = "http://localhost:8000/predict_image"

# URL for the text-based fake news prediction
#API_URL_TEXT = "http://localhost:8000/predict_text"

import base64

def load_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        base64_str = base64.b64encode(img_file.read()).decode("utf-8")
    return base64_str

image_path = "logo.png"
base64_image = load_image_as_base64(image_path)

st.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <!-- Conteneur de l'image -->
        <div style="flex: 1;">
            <img src="data:image/png;base64,{base64_image}" alt="Logo" style="max-width: 100%; height: auto; width: 200px;">
        </div>
        <!-- Conteneur du texte -->
        <div style="flex: 2; padding-left: 20px;">
            <h1 style="text-align: left; color: purple; margin: 0;">Welcome to The Fake News Detector Application</h1>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.text("")
st.text("")

def extract_images_from_screenshot(image):
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Appliquer le seuillage pour trouver les contours
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Trouver les contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_regions = []
    for contour in contours:
        # Obtenir les coordonnées du rectangle englobant
        x, y, w, h = cv2.boundingRect(contour)

        # Filtrer les petites régions et celles avec un rapport d'aspect extrême
        if w < 100 or h < 100 or w/h > 20 or h/w > 20:
            continue

        # Extraire la région potentiellement contenant une image
        region = image[y:y+h, x:x+w]

        # Appliquer OCR pour vérifier si la région contient principalement du texte
        text = pytesseract.image_to_string(region)
        if len(text.strip()) > 5:  # Ignorer les régions avec beaucoup de texte
            continue

        # Calculer la densité de pixels non blancs (comme indicateur de contenu d'image)
        non_white_pixels = cv2.countNonZero(cv2.cvtColor(region, cv2.COLOR_BGR2GRAY))
        density = non_white_pixels / (w * h)
        if density < 0.3:  # Ignorer les régions avec faible densité de contenu (souvent des lettres)
            continue

        # Ajouter la région comme une image intégrée
        image_regions.append(region)

    return image_regions

def extract_text_from_image(image):
    # Convertir en niveaux de gris et faire l'OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text.strip()

def analyze_image_with_api(image):
    # Convertir l'image en fichier binaire
    img_bytes = BytesIO()
    Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)).save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    # Envoyer l'image à l'API
    response = requests.post(API_URL, files={"file": ("image.png", img_bytes, "image/png")})

    if response.status_code == 200:
        result = response.json()
        prediction = result.get("prediction")
        confidence = result.get("confidence")

        if prediction == "sd":
            prediction_name = "Stable Diffusion"
        elif prediction == "dalle":
            prediction_name = "DALL-E"
        elif prediction == "mj":
            prediction_name = "Mid Journey"
        else:
            prediction_name = "real"

        return prediction, confidence, prediction_name
    else:
        st.error(f"Failed to get prediction. Status code: {response.status_code}")
        st.write(response.text)
        return None, None, None

def check_fake_news_on_google(text):
    # Limiter la recherche aux premiers résultats pour éviter une surcharge
    query = f'"{text}"'

    try:
        results = list(search(query, num_results=5))  # Limiter à 5 résultats
        
        if results:
            # Concaténer les résultats pour OpenAI
            combined_results = "\n".join(results)
            
            # Vérifier la présence de sources fiables
            trusted_sources = [
                "france24.com", "minnpost.com", "factcheck.org", "snopes.com",
                "afp.com", "lemonde.fr/verification", "reuters.com/fact-check"
            ]
            
            # Identifier les sources fiables présentes dans les résultats
            detected_trusted_sources = [url for url in results if any(source in url for source in trusted_sources)]
            
            # Préparer la réponse au format JSON
            response = {
                "combined_results": combined_results,
                "detected_trusted_sources": detected_trusted_sources,
                "trusted_sources": trusted_sources
            }

            if detected_trusted_sources:
                st.success("👍🏻 Trusted verification sources found in the results.")
            else:
                st.info("No trusted verification sources found.")

            return response
        else:
            st.write("Aucun résultat trouvé.")
            return {
                "combined_results": "",
                "trusted_sources": []
            }
    except Exception as e:
        st.error(f"Erreur lors de la recherche Google : {e}")
        return {
            "combined_results": "",
            "trusted_sources": [],
            "error": str(e)
        }


############# Interface Streamlit ####################

uploaded_file = st.file_uploader("Upload your screenshot or image!", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Charger l'image avec PIL, vérifier et convertir pour OpenCV en BGR
    image = Image.open(uploaded_file)
    image_rgb = np.array(image)  # Conversion en format RGB natif
    #st.image(image_rgb, caption="Image d'origine en RGB", use_container_width=False, width=200)  # Afficher pour vérifier les couleurs

    # Convertir l'image pour OpenCV en BGR
    image_cv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Extraire les images et le texte intégrés
    embedded_images = extract_images_from_screenshot(image_cv)
    extracted_text = extract_text_from_image(image_cv)

    # Affichage en colonnes
    st.markdown("### Results of extraction and analysis:")
    col1, col2 = st.columns(2)

    with col1:
        # Vérifier s'il y a des images extraites
        if embedded_images:
            st.warning("Image(s) detected.")
            for idx, img in enumerate(embedded_images):
                # Afficher l'image extraite
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                st.image(img_rgb, caption=f"Image integrated {idx + 1}", use_container_width=True)

                # Analyser l'image extraite
                prediction, confidence, prediction_name = analyze_image_with_api(img)

                if prediction:
                    if prediction == "real":
                        st.success("This image looks real 👍🏻")
                    else:
                        st.success(f"This image looks AI producted 🤖⚙️🤖")

                    st.write(f"Confidence : {confidence * 100:.2f}% 🦾")
        else:
            st.warning("No image detected.")

    with col2:
        if not extracted_text:
            st.warning("No text detected.")
        else:
            st.warning("Text detected")
            
            # Analyse du texte avec le modèle textuel
            response = requests.post(API_URL_TEXT, json={"text": extracted_text})

            if response.status_code == 200:
                prediction = response.json().get("prediction")
                confidence = response.json().get("confidence")

                if prediction == "Fake News":
                    st.error(f"This news seems to be fake! 📰❌")
                else:
                    st.success(f"This news seems to be real! 📰✅")
                st.write(f"Confidence: {confidence * 100:.2f}%")
            else:
                st.error(f"Failed to get prediction. Status code: {response.status_code}")
                st.write(response.text)

    if not extracted_text:
        st.warning("No text detected.")
    else:
        st.markdown("### Your judge ! Here is some help from Google and OpenAI:")
        
        # Afficher les résultats sur Streamlit
        st.warning("Google search:")
        
        # Recherche Google
        google_results = check_fake_news_on_google(extracted_text)

        if google_results["combined_results"]:
            st.write("Voici les résultats trouvés sur Google :")
            
            # Afficher chaque URL individuellement
            for url in google_results["combined_results"].split("\n"):
                st.write(f"- {url}")

            # Afficher les sources fiables détectées
            if google_results["trusted_sources"]:
                sources = google_results["trusted_sources"]
                st.write(f"Trusted sources used : {sources}")
            else:
                st.info("Aucune source de vérification fiable détectée.")
        else:
            st.error("No results on Google.")
                
        # Enrichir le texte avec les résultats de recherche pour OpenAI
        enriched_text = f"{extracted_text}\n\nContext from Google Search:\n{google_results}"
        st.warning("OpenAI 👉 Enriching the text with Google Search results for openAI search (gpt-4o model used)...")

        # Appel OpenAI
        openai_response = openai_call_for_fakenews_check(enriched_text)

        if openai_response:
            st.markdown(f"\n{openai_response}")
        else:
            st.error("Failed to get a response from OpenAI.")

    

