import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

def get_images_from_url(url):
    # Récupérer le contenu de la page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraire les URLs d'images
    img_urls = []
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:
            # Si le lien est relatif, le convertir en lien absolu
            if not img_url.startswith('http'):
                img_url = requests.compat.urljoin(url, img_url)
            img_urls.append(img_url)
    return img_urls

def display_images(img_urls):
    # Afficher les images avec la possibilité de les supprimer
    remaining_imgs = []
    for img_url in img_urls:
        response = requests.get(img_url)
        image = Image.open(BytesIO(response.content))
        
        # Afficher l'image et un bouton pour la supprimer
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(image, caption=img_url, use_column_width=True)
        with col2:
            if st.button("Supprimer", key=img_url):
                continue  # Ignorer cette image
            remaining_imgs.append(img_url)  # Garder cette image
    return remaining_imgs

# Interface Streamlit
st.title("Extraction d'images depuis une URL")

# Saisie de l'URL par l'utilisateur
url = st.text_input("Entrez l'URL de la page web :")

if url:
    img_urls = get_images_from_url(url)
    st.write(f"Images trouvées : {len(img_urls)}")

    # Afficher et gérer les suppressions d'images
    if img_urls:
        st.write("Sélectionnez les images à conserver :")
        remaining_images = display_images(img_urls)
        
        st.write("Images sélectionnées (URLs) :")
        st.write(remaining_images)
