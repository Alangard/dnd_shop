# Dockerfile
FROM ubuntu:22.04

EXPOSE 6000 80

# читаем переменные среды из .env
ARG EMAIL_HOST_USER
ARG DOMAIN

# устанавливаем переменные среды в переменные
ENV EMAIL_HOST_USER=$EMAIL_HOST_USER
ENV DOMAIN=$DOMAIN

WORKDIR /certbot
COPY . /certbot
WORKDIR /certbot

RUN apt-get update
RUN apt-get -y install certbot

# запускаем скрипт генерации
CMD ["sh", "generate-certificate.sh"]