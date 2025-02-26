FROM rasa/rasa:3.6.21
WORKDIR /app

COPY ./requirements.txt ./

USER root

RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_md

COPY ./. /app/

RUN  rasa train 

VOLUME /app/models

CMD [ "run","-m","/app/models","--enable-api","--cors","*","--debug" ,"--endpoints", "endpoints.yml", "--log-file", "out.log", "--debug"]

EXPOSE 5005