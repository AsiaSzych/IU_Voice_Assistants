FROM rasa/rasa-sdk:3.6.2

WORKDIR /app

COPY ./requirements.txt ./

USER root

RUN pip install -r requirements.txt

COPY . /app

USER 1001