import openai
import requests
import json
from dotenv import load_dotenv
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

## Charger la clé API
# Charger le fichier .env
load_dotenv()
API_KEY = os.getenv('OPENAI_BEN_API_KEY')
# Get key
if API_KEY:
    print(f"Votre clé API est : {API_KEY}")
else:
    print("Erreur : OPENAI_BEN_API_KEY n'est pas défini.")
    
## Défine API url
url = "https://api.openai.com/v1/chat/completions"

## Défine request header
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def api_key_testing():
    print(API_KEY)


## Fonction pour analyser un texte
def openai_call_for_fakenews_check(text):
    ## Define prompt
    prompt = f"""
        Vous êtes un assistant expert en vérification des faits.
        Analysez le texte ci-dessous et attribuez un score de confiance (entre 0 et 100%) pour chacune des catégories suivantes :
        - VRAI : le texte est factuellement correct et basé sur des preuves solides.
        - POSSIBLE : le texte pourrait être vrai mais manque de preuves suffisantes.
        - PROBABLE : le texte semble crédible mais ne peut pas être entièrement confirmé. 
        Ne reponds pas toujorus 0%, 70% et 30% !! Reflechis sur la base de tes connaissances. Quand quelque chose est possible, on ne peut pas avoir un score "VRAI" à 0% mais au moins supérieur car crédible.
        Pars du principe qu'une reponse possible est très probablement vrai.
        
        Fournissez également une brève justification (moins de 100 mots) pour vos scores.

        Texte : "{text}"

        Réponse attendue au format suivant :
        - VRAI : X% 
        - POSSIBLE : Y%
        - PROBABLE : Z%
        Justification : [votre justification ici]
    """
    
    ## Define model call settings
    data = {
        "model": "gpt-4o",  # Utilisez le modèle disponible
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in detecting fake news."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,  # Limiter la réponse à quelques tokens
        "temperature": 0  # Réponses déterministes
    }

    # Envoyez la requête POST
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Analysez la réponse
    if response.status_code == 200:
        result = response.json()
        print("Response:", result["choices"][0]["message"]["content"])
    else:
        print(f"Erreur : {response.status_code}")
        print("Détails :", response.text)
        

    try:
        # Envoyer la requête POST
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Lève une exception pour les statuts HTTP >= 400

        # Parse la réponse JSON
        result = response.json()
        logging.debug(f"Réponse complète : {result}")

        # Retourner le contenu pertinent
        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        # Capturer et loguer les erreurs
        logging.error(f"Erreur lors de la requête : {str(e)}")
        logging.error(f"Détails de la réponse : {response.text if 'response' in locals() else 'Pas de réponse'}")
        return None