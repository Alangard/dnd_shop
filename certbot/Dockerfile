# Dockerfile
FROM ubuntu:22.04

EXPOSE 6000 80

WORKDIR /certbot
COPY . /certbot
WORKDIR /certbot

RUN apt-get update
RUN apt-get -y install certbot

# запускаем скрипт генерации
CMD ["sh", "generate-certificate.sh"]