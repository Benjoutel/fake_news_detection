FROM python:3.10-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY files files
COPY model.keras model.keras
COPY front.py front.py
COPY main.py main.py

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
