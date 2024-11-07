## First app use

Create local env with 3.10.6 python version, and activate it.

    pyenv virtualenv 3.10.6 myenv
    pyenv local myenv

Install dependancies

    pip install -r requirements.txt

Install the package

    pip install -e .

### Regular setup updates

Reload direnv when you modify the .env file or .envrc file :

    direnv reload





## Choose container for streamlit

### Select the API_URL in main.py

url to use to test the deployed container :

    API_URL = "https://fake-news-image-863060191445.europe-west1.run.app/predict"

url to use for local testing :

    API_URL = "http://localhost:8081/predict" 

    ⚠️ Adapt url with the local port you use. 

