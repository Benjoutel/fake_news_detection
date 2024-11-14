FROM python:3.10-slim

COPY packages.txt packages.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


RUN python -m nltk.downloader stopwords
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY files files
COPY my_model.keras my_model.keras
COPY model.keras model.keras
COPY front.py front.py
COPY main.py main.py

CMD uvicorn main:app --host 0.0.0.0 --port 8080
