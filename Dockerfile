FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y software-properties-common

WORKDIR /code

RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt

RUN add-apt-repository ppa:certbot/certbot
RUN apt-get update && apt-get install -y certbot

COPY . /code/


