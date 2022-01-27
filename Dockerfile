# syntax=docker/dockerfile:1

FROM --platform=linux/amd64 python:3.7-slim-buster

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install git

RUN apt-get -y install python-dev 
RUN apt-get -y install python3-dev 
RUN apt-get -y install libevent-dev

RUN apt-get -y download https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/brown.zip
RUN apt-get -y download https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip -o Dir::Cache="D:"

RUN pip3 install --upgrade pip
RUN pip3 install setuptools wheel

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD python app.py 