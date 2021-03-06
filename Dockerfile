FROM python:3.9

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install xvfb
RUN apt-get update && apt-get install -y software-properties-common unzip curl xvfb

# move project
RUN mkdir /code
COPY ./requirements.txt /code/requirements.txt


# set display port to avoid crash
ENV DISPLAY=:99
ENV RUN_IN_DOCKER True

WORKDIR /code

# upgrade pip
RUN pip install --upgrade pip


# install dependencies
RUN pip install -r requirements.txt