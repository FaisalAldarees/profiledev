FROM python:3.8.3-buster

LABEL maintainer="fsaldarees@profile.dev"

ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get -q update && apt-get clean && rm -rf /var/lib/apt/lists/*

# Setup directory structure
RUN mkdir /app
WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .
