# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .db_functions import check_reservations_in_db, recommend_restaurants


CITY_VALIDATION =  ['Gdańsk', 'Gdynia', "Sopot", "Tricity"]
CUISINE_VALIDATION = ["Italian", "Turkish", "Indian", "Chinese", "sushi", "pizza", "Mexican", "Japanese", "French"]

class ActionFetchReservations(Action):

    def name(self) -> Text:
        return "action_fetch_reservations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        full_name = tracker.get_slot("PERSON")
        current_reservations_message = check_reservations_in_db(full_name)
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
            restaurant_name = recommend_restaurants(city, cuisine)
            dispatcher.utter_message(text=f"I have found a {restaurant_name} restaurant in {city}")

        return []