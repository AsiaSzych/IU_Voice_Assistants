# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .db_functions import check_reservations_in_db


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
        
        dispatcher.utter_message(text="I have found a XYZ restaurant, is that okay?")

        return []