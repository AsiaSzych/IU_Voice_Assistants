## Should be run from root project directory with folder selection:
#  rasa run actions --actions rasa_chatbot.actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from database.db_queries import get_reservations, get_restaurant_recommendations

DB_PATH = 'database/restaurants.db'
CITY_VALIDATION =  ['Gdańsk', 'Gdynia', "Sopot", "Tricity"]
CUISINE_VALIDATION = ["Italian", "Turkish", "Indian", "Chinese", "sushi", "pizza", "Mexican", "Japanese", "French"]

class ActionFetchReservations(Action):

    def name(self) -> Text:
        return "action_fetch_reservations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        full_name = tracker.get_slot("PERSON")
        amount_of_reservations = get_reservations(full_name, db_path=DB_PATH)
        current_reservations_message = f"Currently there are {amount_of_reservations} reservations for {full_name}"
        dispatcher.utter_message(text=current_reservations_message)

        return []


class ActionFindRestaurant(Action):

    def name(self) -> Text:
        return "action_find_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = tracker.get_slot("GPE")
        cuisine = tracker.get_slot("cuisine")
        if city not in CITY_VALIDATION:
            dispatcher.utter_message("I'm sorry. It is only possible to find restaurant in the Tricity area of Poland")
            # return empty city slot
        elif cuisine not in CUISINE_VALIDATION:
            dispatcher.utter_message("I'm sorry, I don't have any restaurant with such a cuisine. Please try something else")
            # return empty cuisine slot
        else:
            restaurant_id, restaurant_name = get_restaurant_recommendations(city, cuisine, db_path=DB_PATH)
            dispatcher.utter_message(text=f"I have found a {restaurant_name} restaurant in {city}")

        return []