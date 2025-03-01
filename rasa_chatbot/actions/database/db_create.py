import psycopg2
from .db_config import DB_CONFIG 

conn = psycopg2.connect(
    host=DB_CONFIG['host'],
    database=DB_CONFIG['database'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password']
)
cursor = conn.cursor()

# Create restaurants table
cursor.execute('''
CREATE TABLE IF NOT EXISTS restaurants (
    restaurant_id SERIAL PRIMARY KEY, 
    city VARCHAR NOT NULL,
    place_id VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    cuisine VARCHAR,
    address VARCHAR,
    phone VARCHAR,
    price_level FLOAT,
    avg_rating FLOAT,
    amount_of_ratings FLOAT,
    vegetarian BOOLEAN,
    beer BOOLEAN,
    wine BOOLEAN,
    opening_hours VARCHAR,
    tags TEXT
);
''')
print("restaurants table created successfully")

# Create reservations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    restaurant_id VARCHAR REFERENCES restaurants(place_id),
    name VARCHAR NOT NULL,
    num_people INT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    phone VARCHAR
);
''')
print("reservations table created successfully")

# Commit and close connection
conn.commit()
conn.close()
