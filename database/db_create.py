import sqlite3

conn = sqlite3.connect("restaurants.db")
cursor = conn.cursor()

# Create restaurants table
cursor.execute('''
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id TEXT UNIQUE NOT NULL,
    city TEXT NOT NULL,
    name TEXT NOT NULL,
    cuisine TEXT,
    address TEXT,
    phone TEXT,
    price_level INTEGER,
    avg_rating REAL,
    amount_of_ratings INTEGER,
    vegetarian BOOLEAN,
    beer BOOLEAN,
    wine BOOLEAN,
    opening_hours TEXT,
    tags TEXT
);
''')
print("restaurants table created sucessfully")

# Create reservations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    num_people INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    phone TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);
''')
print("reservations table created sucessfully")

conn.commit()

conn.close()