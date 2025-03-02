import psycopg2
import logging
from .db_config import DB_CONFIG 

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db_queries")

def connect_to_db():
    """Create a connection to the PostgreSQL database."""
    return psycopg2.connect(
    host=DB_CONFIG['host'],
    database=DB_CONFIG['database'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password']
)

def get_restaurants(city):
    logger.debug(f"get_restaurants query for city {city}")
    conn = connect_to_db()
    query = """
    SELECT place_id, name, cuisine, avg_rating, price_level, vegetarian, beer, wine 
    FROM restaurants 
    WHERE city = %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_reservations(city):
    logger.debug(f"get_reservations query for city {city}")
    conn = connect_to_db()
    query = """
    SELECT place.place_id, place.name, res.name AS user_name
    FROM restaurants place
    JOIN reservations res ON place.place_id = res.restaurant_id
    WHERE place.city = %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_distinct_users_in_city(city):
    logger.debug(f"get_distinct_users_in_city query for city {city}")
    conn = connect_to_db()
    query = """
    SELECT DISTINCT res.name 
    FROM restaurants place
    JOIN reservations res ON place.place_id = res.restaurant_id
    WHERE place.city = %s;
    """
    cursor = conn.cursor()
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    conn.close()
    return data

def make_reservation(restaurant_id, name, num_people, date, time):
    logger.debug(f"make_reservation query for restaurant_id {restaurant_id}")
    conn = connect_to_db()
    cursor = conn.cursor()

    # Check if the user already has a reservation on the same date
    user_check_query = '''
    SELECT COUNT(*) FROM reservations
    WHERE restaurant_id = %s AND name = %s AND date = %s;
    '''
    cursor.execute(user_check_query, (restaurant_id, name, date))
    user_reservations = cursor.fetchone()[0]

    if user_reservations > 0:
        cursor.close()
        conn.close()
        return "user_exists"  # Indicate user already has a reservation

    # Check if the restaurant already has 3 reservations at the same date and time
    time_check_query = '''
    SELECT COUNT(*) FROM reservations
    WHERE restaurant_id = %s AND date = %s AND time = %s;
    '''
    cursor.execute(time_check_query, (restaurant_id, date, time))
    existing_reservations = cursor.fetchone()[0]

    if existing_reservations >= 3:
        cursor.close()
        conn.close()
        return "time_full"  # Indicate restaurant is fully booked at that time

    # Insert new reservation if all checks pass
    insert_query = '''
    INSERT INTO reservations (restaurant_id, name, num_people, date, time)
    VALUES (%s, %s, %s, %s, %s);
    '''
    cursor.execute(insert_query, (restaurant_id, name, num_people, date, time))
    conn.commit()
    cursor.close()
    conn.close()
    return "success"

def get_closest_reservation_for_user(name):
    logger.debug(f"get_closest_reservation_for_user query for user {name}")

    query_closest_future = '''
    SELECT restaurant_id, date, time, num_people, 
           EXTRACT(EPOCH FROM (date::timestamp - CURRENT_TIMESTAMP)) as date_diff
    FROM reservations
    WHERE name = %s AND date >= CURRENT_DATE
    ORDER BY date_diff 
    '''
    query_closest_past = '''
    SELECT restaurant_id, date, time, num_people, 
            EXTRACT(EPOCH FROM (date::timestamp - CURRENT_TIMESTAMP))as date_diff
    FROM reservations
    WHERE name = %s AND date < CURRENT_DATE
    ORDER BY date_diff 
    '''

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query_closest_future, (name,))
    results = cursor.fetchall()
    if len(results) > 0:
        closest_resevation = results[0]
        text = "is"
    else:
        cursor.execute(query_closest_past, (name,))
        results = cursor.fetchall()
        if len(results) > 0:
            closest_resevation = results[0]
            text = "was"
        else:
            closest_resevation = []
            text = "no"

    conn.close()
    logger.debug(f"Found {results} reservations for {name}")
    return closest_resevation, text

def get_restaurant_name(restaurant_id):
    logger.debug(f"get_restaurant_name query for restaurant_id {restaurant_id}")
    query = '''
    SELECT name
    FROM restaurants
    WHERE place_id = %s
    '''

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query, (restaurant_id,))
    results = cursor.fetchall()
    conn.close()
    return results[0][0]

def get_restaurant_details(restaurant_id):
    logger.debug(f"get_restaurant_details query for restaurant_id {restaurant_id}")
    conn = connect_to_db()
    query = """
    SELECT place_id, name, cuisine, avg_rating, price_level, vegetarian, beer, wine 
    FROM restaurants 
    WHERE place_id = %s
    """
    cursor = conn.cursor()
    cursor.execute(query, (restaurant_id,))
    data = cursor.fetchall()
    conn.close()
    return data


if __name__ == "__main__":
    # Test queries
    print(get_reservations("Sopot"))
    print(get_restaurants("Sopot"))
    print(get_distinct_users_in_city("Gdynia"))
    print(get_restaurant_name("ChIJK4PtjPun_UYRRYuECz2jxWk"))
    print(get_restaurant_details("ChIJK4PtjPun_UYRRYuECz2jxWk"))
    print(get_closest_reservation_for_user("Joanna Szych"))
    print(make_reservation("ChIJ90grTyOn_UYRYV0USPJmPq4", "John Doe", 4, "2025-02-10", "15:00"))
    print(make_reservation("ChIJ90grTyOn_UYRYV0USPJmPq4", "Mike Brown", 4, "2025-02-10", "15:00"))
    print(make_reservation("ChIJ90grTyOn_UYRYV0USPJmPq4", "Susan Geller", 4, "2025-02-10", "15:00"))
    print(make_reservation("ChIJ90grTyOn_UYRYV0USPJmPq4", "Ross Geller", 4, "2025-02-10", "15:00"))