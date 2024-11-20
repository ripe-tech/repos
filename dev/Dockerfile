FROM python:3.12-alpine

RUN apk update &&\
    apk add --no-cache \
        bash \
        ca-certificates \
        git \
        sudo \
        wget

# Install watchmedo for code reloading
RUN pip install watchdog==5.0.3

WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extra.txt .
RUN pip install -r extra.txt

# Get working directory properly filled up
COPY src /src
