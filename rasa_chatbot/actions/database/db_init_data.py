import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db_init")

conn = sqlite3.connect("restaurants.db")
cursor = conn.cursor()

def load_all_restaurants_from_csv(csv_file):
    
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";", header=0, index_col=0)

    # Convert boolean-like column into real booleans
    df["Vegetarian"] = df["Vegetarian"].astype(bool)
    df["Beer"] = df["Beer"].astype(bool)
    df["Wine"] = df["Wine"].astype(bool)

    # Rename columns to match database schema
    df.rename(columns={
        "City": "city",
        "Place_ID": "place_id",
        "Place_Name": "name",
        "Cuisine": "cuisine",
        "Address": "address",
        "Phone Number": "phone",
        "Price level": "price_level",
        "Avg rating": "avg_rating",
        "Amount of ratings": "amount_of_ratings",
        "Vegetarian": "vegetarian",
        "Beer": "beer",
        "Wine": "wine",
        "Opening Hours": "opening_hours",
        "tags": "tags"
    }, inplace=True)

    df.to_sql("restaurants", conn, if_exists="replace", index=False, method="multi")

    logger.debug(f"Loaded {len(df)} restaurants into the database!")


def load_initial_reservations(csv_file):

    df = pd.read_csv(csv_file, encoding="utf-8", sep=";", header=0, index_col=0)

    df.to_sql("reservations", conn, if_exists="replace", index=False, method="multi")

    logger.debug(f"Loaded {len(df)} reservations into the database!")


if __name__ == "__main__":
    load_all_restaurants_from_csv("../restaurants_data/all_restaurants_info.csv") 
    load_initial_reservations("../restaurants_data/initial_reservations.csv")

conn.close()