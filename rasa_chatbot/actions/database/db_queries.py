import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db_queries")


def get_restaurants(city, db_path="restaurants.db"):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT place_id, name, cuisine, avg_rating, price_level, vegetarian, beer, wine 
    FROM restaurants 
    WHERE city = ?;
    """
    cursor = conn.cursor()
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_reservations(city, db_path="restaurants.db"):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT place.place_id, place.name, res.name AS user_name
    FROM restaurants place
    JOIN reservations res ON place.place_id = res.restaurant_id
    WHERE place.city = ?;
    """
    cursor = conn.cursor()
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_distinct_users_in_city(city, db_path="restaurants.db"):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT DISTINCT res.name 
    FROM restaurants place
    JOIN reservations res ON place.place_id = res.restaurant_id
    WHERE place.city = ?;
    """
    cursor = conn.cursor()
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    conn.close()
    return data

#TODO: change this - add logic to check if there is a possibility to make reservation
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

def get_closest_reservation_for_user(name, db_path="restaurants.db", *kwargs):

    query_closest_future = '''
    SELECT restaurant_id, date, time, num_people,  julianday(date) - julianday('now') AS date_diff
    FROM reservations
    WHERE name = ? and date_diff >- 0 
    ORDER BY date_diff 
    '''
    query_closest_past = '''
    SELECT restaurant_id, date, time, num_people,  julianday(date) - julianday('now') AS date_diff
    FROM reservations
    WHERE name = ? and date_diff < 0 
    ORDER BY date_diff desc
    '''

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query_closest_future, (name,))
    results = cursor.fetchall()
    if len(results)>0:
        closest_resevation = results[0]
        text = "is"
    else:
        cursor = conn.cursor()
        cursor.execute(query_closest_past, (name,))
        results = cursor.fetchall()
        if len(results)>0:
            closest_resevation = results[0]
            text = "was"
        else:
            closest_resevation = []
            text = "no"

    conn.close()

    logger.debug(f"Found {results} reservations for {name}")

    return closest_resevation, text

def get_restaurant_name(restaurant_id, db_path="restaurants.db"):

    query = '''
    SELECT name
    FROM restaurants
    WHERE place_id = ?
    '''

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, (restaurant_id,))
    results = cursor.fetchall()
    return results[0][0]

def get_restaurant_details(restaurant_id, db_path="restaurants.db"):

    conn = sqlite3.connect(db_path)
    query = """
    SELECT place_id, name, cuisine, avg_rating, price_level, vegetarian, beer, wine 
    FROM restaurants 
    WHERE place_id = ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (restaurant_id,))
    data = cursor.fetchall()
    conn.close()
    return data


if __name__ == "__main__":
    # Test queries
    make_reservation("ChIJ90grTyOn_UYRYV0USPJmPq4", "John Doe", 4, "2025-02-10", "15:00")
    get_reservations("Joanna Szych")
    get_restaurant_name("ChIJK4PtjPun_UYRRYuECz2jxWk")
