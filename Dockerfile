# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8-appservice
FROM python:latest
FROM ubuntu:latest

ENV TZ=Europe/Minsk

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean \
&& apt-get update \
&& apt-get install sudo -y \
&& apt-get install apt-transport-https -y \
&& sudo apt-get install unixodbc -y \
&& sudo apt-get install unixodbc-dev -y \
&& sudo apt-get install curl -y \
&& sudo apt-get install poppler-utils -y \
&& sudo apt-get install --reinstall build-essential -y \
&& sudo apt-get install wget -y


RUN echo "Set disable_coredump false" >> /etc/sudo.conf

RUN sudo su
RUN sudo curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN sudo curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN sudo apt-get update
RUN sudo ACCEPT_EULA=Y apt-get install msodbcsql17
RUN sudo ACCEPT_EULA=Y apt-get install mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc


RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable


RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

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


RUN sudo apt install python3-pip -y

RUN pip3 install -r /requirements.txt

CMD [ "python3", "./LivingWaterScrape.py" ]