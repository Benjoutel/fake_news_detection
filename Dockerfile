FROM python:3.10-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN python -m nltk.downloader stopwords

COPY files files
COPY my_model.keras my_model.keras
COPY model.keras model.keras
COPY front.py front.py
COPY main.py main.py

CMD uvicorn main:app --host 0.0.0.0 --port 8080
