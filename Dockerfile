# syntax=docker/dockerfile:1

FROM --platform=linux/arm64 python:3.7-slim-buster

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install git

RUN apt-get -y install python-dev 
RUN apt-get -y install python3-dev 
RUN apt-get -y install libevent-dev

RUN pip3 install pip setuptools wheel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN python -m spacy download en
RUN python -m spacy download en_core_web_sm

COPY . .

CMD python app.py