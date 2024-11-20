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

## Défine API url
url = "https://api.openai.com/v1/chat/completions"

## Défine request header
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

#def api_key_testing():
#    print(API_KEY)


## Fonction pour analyser un texte
def openai_call_for_fakenews_check(text):
    ## Define prompt
    prompt = f"""
    You are an expert assistant in fact-checking.
    Analyze the text below and provide:
    1. A confidence score (0% to 100%) representing how likely the text is true.
    2. A brief justification (max 50 words) explaining your reasoning.
    3. A final verdict: TRUE if the score is above 50%, FALSE otherwise.

    Respond in this format:
    - Confidence: X%
    - Justification: [Your explanation]
    - Verdict: [TRUE/FALSE]

    Text: "{text}"
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
        logging.error(f"Détails de la réponse : {response.text if 'response' in locals() else 'No response'}")
        return None
