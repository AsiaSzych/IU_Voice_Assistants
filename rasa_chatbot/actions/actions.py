## Should be run from root project directory with folder selection:
#  rasa run actions --actions rasa_chatbot.actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .database.db_queries import get_closest_reservation_for_user, make_reservation, get_restaurant_name
from .database.db_recommendations import get_combined_recommendations
import difflib

CITY_VALIDATION =  ['Gdańsk', 'Gdynia', "Sopot", "Tricity"]
CUISINE_VALIDATION = ["Italian", "Turkish", "Indian", "Chinese", "sushi", "pizza", "Mexican", "Japanese", "French"]

class ActionFetchReservations(Action):

    def name(self) -> Text:
        return "action_fetch_reservations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        full_name = tracker.get_slot("PERSON")
        closest_reservation, text = get_closest_reservation_for_user(full_name)
        if closest_reservation:
            restaurant_id = closest_reservation[0]
            restaurant_name = get_restaurant_name(restaurant_id)
            current_reservations_message = f"Your closest reservation {text} on {closest_reservation[1]} at {closest_reservation[2]} for {closest_reservation[3]} people, in the {restaurant_name}." 
        else:
            current_reservations_message = f'Sorry currently there are no reservations for {full_name}'
        if text == 'was':
            current_reservations_message = current_reservations_message + "There are no reservations in the future."
        dispatcher.utter_message(text=current_reservations_message)

        return []

class ActionMakeReservations(Action):

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
        make_reservation(place, full_name, num_people, date, time=hour)
        dispatcher.utter_message(text=f"I have made a reservation for you, on {date}, {hour}, for {num_people} people")

        return []

class ActionFindRestaurant(Action):

    def name(self) -> Text:
        return "action_find_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        full_name = tracker.get_slot("PERSON")
        city = tracker.get_slot("GPE")
        cuisine = tracker.get_slot("cuisine")
        pricing_level = tracker.get_slot("pricing_level")
        rating_level = tracker.get_slot("rating_level")
        vege = tracker.get_slot("vegetarian") # bool
        alcohol = tracker.get_slot("alcohol") # bool

        addiitonal_options = {}
        if pricing_level:
            addiitonal_options.update({"price_level": pricing_level})
        if rating_level:
            addiitonal_options.update({"avg_rating": rating_level})
        if vege:
            addiitonal_options.update({"vegetarian": 1})
        if alcohol:
            addiitonal_options.update({"beer": 1})
            addiitonal_options.update({"wine": 1})

        if city not in CITY_VALIDATION:
            dispatcher.utter_message("I'm sorry. It is only possible to find restaurant in the Tricity area of Poland")
            # return empty city slot
        elif cuisine not in CUISINE_VALIDATION:
            dispatcher.utter_message("I'm sorry, I don't have any restaurant with such a cuisine. Please try something else")
            # return empty cuisine slot
        else:
            first, second, third = get_combined_recommendations(city, cuisine, optional_filters=addiitonal_options)
            restaurant_id, restaurant_name, _ = first 
            dispatcher.utter_message(text=f"I have found a {restaurant_name} restaurant in {city}")
            
        return [SlotSet("place_id", restaurant_id),SlotSet("place_name", restaurant_name) ]

class ActionMapFiltersToScale(Action):
    def name(self):
        return "action_map_filters"

    def run(self, dispatcher, tracker, domain):
        # Get user-provided slots
        pricing_text = tracker.get_slot("pricing")
        rating_text = tracker.get_slot("rating")
        vege = tracker.get_slot("vegetarian") # bool
        alcohol = tracker.get_slot("alcohol") # bool

        # Pricing Mapping (1 = Cheap, 2 = Moderate, 3 = Expensive)
        pricing_mapping = {
            "cheap": 1, "budget-friendly": 1, "budget": 1, "not too pricey": 1, "affordable": 1, "low-cost": 1, "not expensive": 1,
            "mid-range": 2, "moderately priced": 2, "fair prices": 2, "reasonably priced": 2, "not too cheap, not too expensive": 2,
            "expensive": 3, "high-end": 3, "luxury": 3, "fine dining": 3, "fancy": 3, "premium": 3, "upscale": 3
        }

        # Rating Mapping (>4.0 = Good, >3.0 = Decent)
        rating_mapping = {
            "highly-rated": 4.0, "high ratings":4.5, "good rating": 4.0, "best-rated": 4.5, "top-rated": 4.5, "solid reputation": 4.0,
            "great reviews": 4.0, "well-rated": 4.0, "decent rating": 3.0, "recommended": 4.0, "proven place": 4.0
        }

        # Function to perform fuzzy matching
        def fuzzy_match(input_text, mapping):
            if not input_text:
                return None
            input_text = input_text.lower()
            if input_text in mapping:
                return mapping[input_text]
            closest_match = difflib.get_close_matches(input_text, mapping.keys(), n=1, cutoff=0.6)
            return mapping[closest_match[0]] if closest_match else None

        # Process Pricing
        pricing_level = fuzzy_match(pricing_text, pricing_mapping)

        # Process Rating
        rating_threshold = fuzzy_match(rating_text, rating_mapping)

        # Generate Response
        response_parts = []
        if pricing_level:
            response_parts.append(f"price level {pricing_level}")
        if rating_threshold:
            response_parts.append(f"rating above {rating_threshold}")
        if vege:
            response_parts.append(f"vegetarian options")
        if alcohol:
            response_parts.append(f"alcohol available")

        if response_parts:
            dispatcher.utter_message(text=f"Got it! I'll look for restaurants with {', '.join(response_parts)}.")
        else:
            dispatcher.utter_message(text="I couldn't understand your preferences. Could you clarify?")

        return [
            SlotSet("pricing_level", pricing_level),
            SlotSet("rating_level", rating_threshold)
        ]