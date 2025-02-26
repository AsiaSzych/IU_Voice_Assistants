# IU_Voice_Assistants

Voice Assistant for handling restaurant related requests, developed as a student project. 

## Assumptions

Handles chosen restaurants in the area of Tricity, Poland. List od restaurants and their ? is available in the *./restaurants_data/all_restaurants_info.csv* file. 

The bot should allow for 3 main actions:
* Recommending the best suited restaurant based on at least city and cuisine
* Reserving a table in the restaurant (fictional reservation in a project database)
* Informing about already made reservations 


## Usage

Assistant is intented to use as localy deployed voicebot. The setup scripts are prepared for a UNIX based systems. To run the assistant having a working **speakers** and **microphone** is necessary! 

### Steps to run:
1. Create a python3.10 environment 
2. Run a setup.sh script
3. Install requirements from requirements.txt
4. Run docker compose up in the main folder ??
5. Run the va_main.py python script

### Docker compose 
Docker componse creates the environment for rasa chatbot. It consists of 3 services:
* **duckling** server for entity extraction - from [rasa/duckling](https://hub.docker.com/r/rasa/duckling) 
* **actions** server that hosts rasa actions - build by dockerfile in */rasa_chatbot/actions*, stored on [aszych/iu_rasa_actions](https://hub.docker.com/u/aszych)
* **rasa** server that hosts rasa chatbot model - build by dockerfile in */rasa_chatbot*, stored on[aszych/iu_rasa_chatbot](https://hub.docker.com/u/aszych)

Those services allow main assistant loop to use chatbot model developed in Rasa software via API. ??

### Chatbot instead of Voicebot 

Since voice assistant is based on rasa chatbot, there is a possibility to run and "talk" with the chatbot itself, skiping the voice component. To do this, one can either:
* run docker compose up
* query rasa API using ```curl -XPOST http://localhost:5005/webhooks/rest/webhook   -H "Content-type: application/json"   -d '{"sender": "test", "message": "Hi. Whta's up"}'```

OR 

* start duckling server separately, running `docker run -p 8000:8000 rasa/duckling`
* start action server separately `docker run -p 5055:5055 aszych/iu_rasa_actions`
* start rasa chatbotin the shell, from the */rasa_chatbot* folder run `rasa shell`

[comment]: <> (# Workflow - description)