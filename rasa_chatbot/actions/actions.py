## Should be run from root project directory with folder selection:
#  rasa run actions --actions rasa_chatbot.actions
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import ValidationAction
from typing import Any, Dict, Text

from .database.db_queries import get_closest_reservation_for_user, make_reservation, get_restaurant_name
from .database.db_recommendations import get_combined_recommendations
import difflib

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

        if not (full_name and num_people and time and place):
            dispatcher.utter_message(text="I'm missing some details for your reservation. Could you please provide all necessary information?")
            return []

        date = time.split("T")[0]
        hour = time.split("T")[1][:5]

        # Attempt to make a reservation
        reservation_status = make_reservation(place, full_name, num_people, date, hour)

        if reservation_status == "success":
            dispatcher.utter_message(text=f"I have made a reservation for you on {date} at {hour} for {num_people} people.")
            return []

        elif reservation_status == "user_exists":
            dispatcher.utter_message(text=f"You already have a reservation at this restaurant on {date}. Please choose a different date.")
            return [SlotSet("time", None), SlotSet("date", None)]  # Reset date & time slots

        elif reservation_status == "time_full":
            dispatcher.utter_message(text=f"Unfortunately, this restaurant is fully booked at {hour} on {date}. Please choose a different date or time.")
            return [SlotSet("time", None), SlotSet("date", None)]  # Reset date & time slots

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
        if not full_name:
            full_name = ""
        try:
            first, _, _ = get_combined_recommendations(city=city, 
                                                                cuisine_preferences=cuisine,
                                                                user_name=full_name,
                                                                optional_filters=addiitonal_options)
            restaurant_id, restaurant_name, _ = first 
            dispatcher.utter_message(text=f"I have found a {restaurant_name} restaurant in {city}")
            return [SlotSet("place_id", restaurant_id),SlotSet("place_name", restaurant_name) ]

        except Exception as e:
            dispatcher.utter_message(text=f"I'm so sorry, there seems to be some issue finding a restaurant for you. Let's try again! ")
            return [SlotSet("full_name", None),SlotSet("city", None), SlotSet("cuisine", None), SlotSet("pricing_level", None), SlotSet("rating_level", None), SlotSet("vege", None), SlotSet("alcohol", None) ]

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
    
class ValidateFindRestaurantForm(ValidationAction):
    def name(self) -> Text:
        return "validate_find_restaurant_form"

    def validate_GPE(
        self, slot_value: Any, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Validate that the provided city is within the supported locations."""

        valid_cities = ["Gdańsk", "Gdynia", "Sopot", "Tricity"]
        city_mapping = {
            "Gdańsk": ["Gdansk", "Gdańsk city", "Danzig", "Gdánsk", "Gdanks"],
            "Gdynia": ["Gdinia", "Gdinya", "Gdynska", "Gdynia city", "Gdyna", "Gdynya"],
            "Sopot": ["Sopott", "Sopod", "Sopot city", "Sopotka"],
            "Tricity": ["Tri-City", "Tri City", "Trójmiasto", "3City", "Three Cities", "3-city", "Trici", "Triciti"]
        }

        # Flatten mapping for easy lookup
        all_variants = {variant.lower(): city for city, variants in city_mapping.items() for variant in variants}

        # Normalize the input
        city_text = slot_value.lower() if slot_value else ""

        # Check for direct match or mapped synonym
        matched_city = all_variants.get(city_text, None)
        if matched_city:
            dispatcher.utter_message(text=f"Got it! I'll find restaurants in {matched_city}.")
            return {"GPE": matched_city}

        # If no match, check if it's a completely unsupported city
        if slot_value not in valid_cities:
            dispatcher.utter_message(text=f"Sorry, I currently support restaurants only in Gdańsk, Gdynia, Sopot, and Tricity. Could you specify one of these?")
            return {"GPE": None}  # Reset the slot and ask again

        return {"GPE": slot_value}

    
    def validate_cuisine(
        self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Validate that the provided cuisine is in the allowed list and map common variations."""

        # valid_cuisines: "Italian", "Turkish", "Indian", "Chinese", "sushi", "pizza", "Mexican", "Japanese", "French"
        cuisine_mapping = {
            "Italian": ["italian", "Itallian", "Itailan", "Itlian", "Itallan", "Italain", "Italien", "Italiano", "Italiani"],
            "Turkish": ["turkish", "Turksh", "Tirkish", "Trukish", "Turckish", "Turkysh"],
            "Indian": ["indian", "Indan", "Indain", "Indiann", "Indyan", "Indiian"],
            "Chinese": ["chinese", "Chnese", "Chinesse", "Chinee", "Chines", "Chinease"],
            "sushi": ["Sushi", "Suschi", "Sushee", "Sushy", "Suhsi", "Sushie"],
            "pizza": ["Pizza", "Piza", "Pizaa", "Pitsa", "Pizaa", "Pizzza"],
            "Mexican": ["mexican", "Mexian", "Mexiacan", "Mexcan", "Mexicann", "Meixcan"],
            "Japanese": ["japanese", "Japaneese", "Japenese", "Japnese", "Japanees", "Jappanese"],
            "French": ["french", "Franch", "Frech", "Frensh", "Frenche"]
        }

        # Flatten mapping for easy lookup
        all_variants = {variant.lower(): cuisine for cuisine, variants in cuisine_mapping.items() for variant in variants}

        # Normalize the input
        cuisine_text = slot_value.lower() if slot_value else ""

        # Check for direct match or mapped synonym
        matched_cuisine = all_variants.get(cuisine_text, None)
        if matched_cuisine:
            dispatcher.utter_message(text=f"Got it! You're looking for {matched_cuisine} cuisine.")
            return {"cuisine": matched_cuisine}

        # If no match, reject and ask again
        dispatcher.utter_message(
            text="Sorry, I only support the following cuisines: Italian, Turkish, Indian, Chinese, sushi, pizza, "
                 "Mexican, Japanese, or French. Could you specify one of these?"
        )
        return {"cuisine": None}  