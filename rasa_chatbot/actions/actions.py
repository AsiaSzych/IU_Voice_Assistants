## Should be run from root project directory with folder selection:
#  rasa run actions --actions rasa_chatbot.actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from database.db_queries import get_closest_reservation_for_user, make_reservation, get_restaurant_name
from database.db_recommendations import get_combined_recommendations

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
        closest_reservation, text = get_closest_reservation_for_user(full_name, db_path=DB_PATH)
        if closest_reservation:
            restaurant_id = closest_reservation[0]
            restaurant_name = get_restaurant_name(restaurant_id, db_path = DB_PATH)
            current_reservations_message = f"Your closest reservation {text} on {closest_reservation[1]} at {closest_reservation[2]} for {closest_reservation[3]} people, in the {restaurant_name}." 
        else:
            current_reservations_message = f'Sorry currently there are no reservations for {full_name}'
        if text == 'was':
            current_reservations_message = current_reservations_message + "There are no reservations in the future."
        dispatcher.utter_message(text=current_reservations_message)

        return []

class ActionFetchReservations(Action):

    def name(self) -> Text:
        return "action_make_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        full_name = tracker.get_slot("PERSON")
        num_people = tracker.get_slot("number")
        time = tracker.get_slot("time")
        place = tracker.get_slot("place_id")
        date = time.split("T")[0]
        hour = time.split("T")[1][:5]
        make_reservation(place, full_name, num_people, date, time=hour, db_path=DB_PATH)
        dispatcher.utter_message(text=f"I have made a reservation for you, on {date}, {hour}, for {num_people} people")

        return []

class ActionFindRestaurant(Action):

    def name(self) -> Text:
        return "action_find_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        full_name = tracker.get_slot("PERSON")
        print(full_name)
        city = tracker.get_slot("GPE")
        cuisine = tracker.get_slot("cuisine")
        if city not in CITY_VALIDATION:
            dispatcher.utter_message("I'm sorry. It is only possible to find restaurant in the Tricity area of Poland")
            # return empty city slot
        elif cuisine not in CUISINE_VALIDATION:
            dispatcher.utter_message("I'm sorry, I don't have any restaurant with such a cuisine. Please try something else")
            # return empty cuisine slot
        else:
            first, second, third = get_combined_recommendations(city, cuisine, db_path=DB_PATH)
            restaurant_id, restaurant_name, _ = first 
            dispatcher.utter_message(text=f"I have found a {restaurant_name} restaurant in {city}")
            
        return [SlotSet("place_id", restaurant_id),SlotSet("place_name", restaurant_name) ]