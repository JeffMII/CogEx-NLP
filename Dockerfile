# syntax=docker/dockerfile:1

FROM --platform=linux/arm64 python:3.8-slim-buster

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install git

RUN apt-get -y install python-dev 
RUN apt-get -y install python3-dev 
RUN apt-get -y install libevent-dev

RUN pip install --upgrade pip
RUN pip install setuptools wheel

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN python -m spacy download en
# RUN python -m spacy download en_core_web_sm

EXPOSE 8000

COPY . .

CMD gunicorn -w 4 -b :8000 app:app
# CMD python app.py