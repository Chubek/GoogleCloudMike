# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8-appservice
FROM python:3.7-slim
RUN mkdir app
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
ADD . ./


ENV TZ=Europe/Minsk

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get clean \
&& apt-get update \
&& apt-get install sudo -y \
&& sudo apt-get install wget -y \
&& sudo apt-get install -y gnupg2 \
&& sudo apt-get install python3-dev -y



RUN echo "Set disable_coredump false" >> /etc/sudo.conf

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable


RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip chromedriver.storage.googleapis.com/84.0.4147.30/chromedriver_linux64.zip
RUN sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN sudo apt-get install python3-lxml -y

ENV DISPLAY=:99



RUN sudo apt install python3-pip -y

RUN pip3 install -r ./requirements.txt

CMD ["python", "ScraperLivingWater.py"]

