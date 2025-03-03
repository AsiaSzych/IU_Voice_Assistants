# IU_Voice_Assistants

Voice Assistant for handling restaurant related requests, developed as a student project. 

## Assumptions

Handles chosen restaurants in the area of Tricity, Poland. List od restaurants and their ? is available in the *./restaurants_data/all_restaurants_info.csv* file. 

The bot should allow for 3 main actions:
* Recommending the best suited restaurant based on at least city and cuisine
  * Cities available to choose from: "Gdańsk", "Gdynia", "Sopot",
  * Cuisines available to choose from: "Italian", "Turkish", "Indian", "Chinese", "sushi", "pizza", "Mexican", "Japanese", "French"
* Reserving a table in the restaurant (fictional reservation in a project database)
* Informing about already made reservations 


## Usage

Assistant is intented to use as localy deployed voicebot. The setup scripts are prepared for a **UNIX** based systems. To run the assistant having a working **speakers** and **microphone** is necessary! 
Also, the assistant is using Google Text-To-Speech API. In order to use there there is a need to:
* Have an account on [Google Could Platform](https://console.cloud.google.com/)
* Have Cloud Text To Speech API enabled - you can check it [here](https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/)
* Create a Service Account - the instruction can be found [here](https://cloud.google.com/iam/docs/service-accounts-create#creating)
* Generate Service Account API key in JSON format - the instruction to do this can be found [here](https://cloud.google.com/iam/docs/keys-create-delete#creating)
* Save generated json file in the main application folder with the name *tts_sa.json*


### Steps to run:
1. Create a python3.10 environment
2. Run a `setup.sh` script to install system dependencies
3. Install requirements from `requirements.txt` file 
`pip install -r requirements.txt`
4. Run `python -m spacy download en_core_web_md` in order to download entity recognition model required for the chatbot.
5. Run `docker compose up` in the main project directory
6. Run `python va_main.py` in the main project directory in separate terminal window.

### Windows usage 
Currently the project was not testes on the Windows environment, due to not having access to such operating system at the moment. However, from my research it seems that the steps should be similar. The only change is in step **2** - there is no need for running *setup.sh* file. Insted interested user should make sure to have [ffmpeg library installed](https://ffmpeg.org/download.html#build-windows)

### Docker compose 
Docker componse creates the environment for rasa chatbot. It consists of 4 services:
* **duckling** server for entity extraction - from [rasa/duckling](https://hub.docker.com/r/rasa/duckling) 
* **actions** server that hosts rasa actions - build by dockerfile in */rasa_chatbot/actions*, stored on [aszych/iu_rasa_actions](https://hub.docker.com/repository/docker/aszych/iu_rasa_chatbot/general)
* **rasa** server that hosts rasa chatbot model - build by dockerfile in */rasa_chatbot*, stored on [aszych/iu_rasa_chatbot](https://hub.docker.com/repository/docker/aszych/iu_rasa_actions/general)
* **postgres** server that host PostgreSQL database with restaurant and reservatios - build by dockerfile in */rasa_chatbot/actions/database*, stored on [aszych/iu_rasa_database](https://hub.docker.com/repository/docker/aszych/iu_rasa_database/general)

Those services allow main assistant loop to use chatbot model developed in Rasa software via API.

### Chatbot instead of Voicebot 

Since voice assistant is based on rasa chatbot, there is a possibility to run and "talk" with the chatbot itself, skiping the voice component. To do this, one can either:
* run docker compose up
* query rasa API using ```curl -XPOST http://localhost:5005/webhooks/rest/webhook   -H "Content-type: application/json"   -d '{"sender": "test", "message": "Hi. What can you do?"}'```

OR 

* in the */rasa_chatbot/config.yaml* file, comment line 31 and uncomment line 32. It should set duckling endpoint to localhost 
* start duckling server separately, running `docker run -p 8000:8000 rasa/duckling`
* in the */rasa_chatbot/actions/database/db_config.py* change to 'host': 'localhost'. It should set connection to postgres on localhost  
* start postgres server, by running 
        `docker run -d 
        --name shared_postgres_container 
        -e POSTGRES_USER=rasa_user 
        -e POSTGRES_PASSWORD=rasa_password 
        -e POSTGRES_DB=rasa_db 
        -p 5432:5432 
        -v rasa_postgres_data:/var/lib/postgresql/data 
        aszych/iu_rasa_database:0.0.x`
* in the */rasa_chatbot/endpoints.yaml* file uncomment lines 13-14 and comment lines 16-17. It should set actions endpont to localhost
* start action server separately `docker run -p 5055:5055 aszych/iu_rasa_actions:0.0.x`
* start rasa chatbot in the shell, from the */rasa_chatbot* folder run `rasa shell`

[comment]: <> (# Workflow - description)
