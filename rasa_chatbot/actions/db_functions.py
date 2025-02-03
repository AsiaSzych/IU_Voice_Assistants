import pandas as pd
import random

RESERVATIONS_DB = {
    "Joanna Szych": "3 reservations (Monday 6PM, Wednesday 8PM, Friday 5PM)",
    "Monica Geller": "1 reservation (Tuesday 4PM)", 
}

RESTAURANTS_FILE = "../restaurants_data/all_restaurants_info.csv"

RESTAURANTS_DB = pd.read_csv(RESTAURANTS_FILE, sep=";", header=0, index_col=0)

def check_reservations_in_db(full_name):
    if full_name in RESERVATIONS_DB.keys():
        current_reservations = RESERVATIONS_DB.get(full_name)
        return f"Here is the list of reservations for {full_name}: {current_reservations}"
    else:
        return f"There are currently no reservations for {full_name}"
    

def recommend_restaurants(city, cuisine, *kwargs):
    cuisine = cuisine.lower()
    good_restaurants = RESTAURANTS_DB.where((RESTAURANTS_DB['City']==city) & (RESTAURANTS_DB['Cuisine'].str.contains(cuisine)==True)).dropna().reset_index(drop=True)
    item_range = len(good_restaurants)
    item = random.randint(0, item_range-1)
    chosen_restaurant = good_restaurants.at[item, "Place_Name"]
    return chosen_restaurant