import psycopg2
import pandas as pd
import logging
from .db_config import DB_CONFIG 

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db_init")

conn = psycopg2.connect(
    host=DB_CONFIG['host'],
    database=DB_CONFIG['database'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password']
)
cursor = conn.cursor()

def load_all_restaurants_from_csv(csv_file):
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";", header=0, index_col=0)

    # Convert boolean-like columns into real booleans
    df["Vegetarian"] = df["Vegetarian"].astype(bool)
    df["Beer"] = df["Beer"].astype(bool)
    df["Wine"] = df["Wine"].astype(bool)
    df["Phone Number"] = df["Phone Number"].astype(str)

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

    # Insert into PostgreSQL
    for i, row in df.iterrows():
        cursor.execute("""
            INSERT INTO restaurants (city, place_id, name, cuisine, address, phone, price_level, avg_rating, 
                                    amount_of_ratings, vegetarian, beer, wine, opening_hours, tags) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, tuple(row))
    
    conn.commit()

    logger.debug(f"Loaded {len(df)} restaurants into the database!")

def load_initial_reservations(csv_file):
    df = pd.read_csv(csv_file, encoding="utf-8", sep=";", header=0, index_col=0)
    df["phone"] = df["phone"].astype(str)

    # Insert into PostgreSQL
    for i, row in df.iterrows():
        cursor.execute("""
            INSERT INTO reservations (restaurant_id, name, num_people, date, time, phone) 
            VALUES (%s, %s, %s, %s, %s, %s);
        """, tuple(row))
    
    conn.commit()

    logger.debug(f"Loaded {len(df)} reservations into the database!")

if __name__ == "__main__":
    load_all_restaurants_from_csv("../../../restaurants_data/all_restaurants_info.csv")
    load_initial_reservations("../../../restaurants_data/initial_reservations.csv")

# Close the connection after all operations
conn.close()
