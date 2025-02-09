import sqlite3
import logging
import random

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db_queries")

#TODO: change this for content based recommendation, kwargs to store additional requirements
def get_restaurant_recommendations(city, cuisine, db_path="restaurants.db", *kwargs):
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
    SELECT place_id, name
    FROM restaurants
    WHERE city = ? AND cuisine LIKE ?
    '''
    cursor.execute(query, (city, f"%{cuisine}%"))
    
    results = cursor.fetchall()
    conn.close()
    choice = random.choice(results) #TODO: change this, for now random - later the most suitable 

    return choice[0], choice[1] #TODO: change this, for now return only id and name - later probably more 

#TODO: change this - adding logic to check if there is a possibility to make reservation
def make_reservation(restaurant_id, name, num_people, date, time, db_path="restaurants.db", *kwargs):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
    INSERT INTO reservations (restaurant_id, name, num_people, date, time)
    VALUES (?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (restaurant_id, name, num_people, date, time))
    
    conn.commit()
    conn.close()
    logger.debug(f"New reservation inserted")

#TODO: Change this - return also latest/closest reservation 
def get_reservations(name, db_path="restaurants.db", *kwargs):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
    SELECT count(*)
    FROM reservations
    WHERE name = ?
    '''

    cursor.execute(query, (name,))
    results = cursor.fetchall()[0][0]
    conn.close()

    logger.debug(f"Found {results} reservations for {name}")

    return results


if __name__ == "__main__":
    # Test queries
    print(get_restaurant_recommendations("Gdańsk", "Italian"))
    make_reservation("ChIJ90grTyOn_UYRYV0USPJmPq4", "John Doe", 4, "2025-02-10", "15:00")
    get_reservations("Joanna Szych")
