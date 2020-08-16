# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8-appservice
FROM python:latest
FROM ubuntu:latest

ENV TZ=Europe/Minsk

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean \
&& apt-get update \
&& apt-get install sudo -y \
&& sudo apt-get install wget -y \
&& sudo apt-get install -y gnupg2 \
&& sudo apt-get install libpq-dev python-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev -y \
&& sudo apt-get install python3-dev -y



RUN echo "Set disable_coredump false" >> /etc/sudo.conf

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable


RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip chromedriver.storage.googleapis.com/85.0.4183.38/chromedriver_linux64.zip
RUN sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN sudo apt-get install python3-lxml -y

ENV DISPLAY=:99

COPY requirements.txt /
ADD requirements.txt /

RUN true

COPY LivingWaterScrape.py /
ADD LivingWaterScrape.py /


RUN true

COPY index_start.txt /
ADD index_start.txt /

RUN true

COPY done_urls.txt /
ADD done_urls.txt /

RUN true

COPY client_secrets.json /
ADD client_secrets.json /


RUN sudo apt install python3-pip -y

RUN pip3 install -r /requirements.txt

CMD [ "python3", "./LivingWaterScrape.py" ]
