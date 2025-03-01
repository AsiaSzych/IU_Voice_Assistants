import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import ast
import numpy as np
from collections import defaultdict
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics.pairwise import cosine_similarity
from .db_queries import get_reservations, get_restaurants, get_distinct_users_in_city


def encode_cuisine(restaurants):

    cuisines = [ast.literal_eval(cuisine) if isinstance(cuisine, str) else [] for cuisine in restaurants['cuisine']]
    cuisine_list = [' '.join(cuisine) for cuisine in cuisines]
    vectorizer = TfidfVectorizer()
    cuisine_vectors = vectorizer.fit_transform(cuisine_list).toarray()
    
    return cuisine_vectors, vectorizer


def create_user_profile(cuisine_vectorizer, user_cuisine, user_optional_filters={}):

    user_vector = []
    cuisine_vector = cuisine_vectorizer.transform([user_cuisine]).toarray().flatten()
    user_vector.extend(cuisine_vector)
    user_options = user_optional_filters.keys()
    if "avg_rating" in user_options:
        user_vector.append(user_optional_filters.get("avg_rating"))
    if "price_level" in user_options:
        user_vector.append(user_optional_filters.get("price_level"))
    if "vegetarian" in user_options:
        user_vector.append(user_optional_filters.get("vegetarian"))
    if "beer" in user_options:
        user_vector.append(user_optional_filters.get("beer"))
    if "wine" in user_options:
        user_vector.append(user_optional_filters.get("wine"))

    return np.array(user_vector)


def create_restaurants_profiles(vectorizer, restaurants_data, optional_filters={}):

    restaurants = []
    options = optional_filters.keys()
    for _, row in restaurants_data.iterrows():
        rest_id, rest_name, cuisine, avg_rating, price_level, vegetarian, beer, wine = row
        cuisine = ast.literal_eval(cuisine) if isinstance(cuisine, str) else []
        cuisine_vector = vectorizer.transform([ ' '.join(cuisine)]).toarray().flatten()
        restaurant_vector = []
        restaurant_vector.extend(cuisine_vector)

        if "avg_rating" in options:
            restaurant_vector.append(avg_rating)
        if "price_level" in options:
            restaurant_vector.append(price_level)
        if "vegetarian" in options:
            restaurant_vector.append(vegetarian)
        if "beer" in options:
            restaurant_vector.append(beer)
        if "wine" in options:
            restaurant_vector.append(wine)
        restaurant_dict = {
            "rest_id": rest_id,
            "rest_name": rest_name,
            "rest_vector": np.array(restaurant_vector)}
        restaurants.append(restaurant_dict)

    return restaurants


def calculate_cosine_similarity_user_restaurants(user_profile, restaurants_data):

    #iterating one-by-one is not super optimal - maybe to rethink later
    for restaurant in restaurants_data:
        score = cosine_similarity([user_profile], [restaurant.get("rest_vector")])[0][0]
        restaurant.update({"score": score})

    return restaurants_data


def get_restaurants_content_based(city, 
                                  cuisine_preferences, 
                                  optional_filters={},
                                  amount_of_results=3):
    #get restaurants data
    restaurants_data = get_restaurants(city)

    #not optimal - maybe to rethink
    restaurants_data = pd.DataFrame(restaurants_data, columns=["rest_id", "rest_name", "cuisine", "avg_rating", "price_level", "vegetarian", "beer", "wine"])
    
    #prepare vectoros to compare
    cuisine_vectors, vectorizer = encode_cuisine(restaurants_data)
    user_profile = create_user_profile(vectorizer, cuisine_preferences, optional_filters)
    restaurants_profiles = create_restaurants_profiles(vectorizer, restaurants_data, optional_filters)
    
    #calculate cosine similarity
    restaurants_with_score = calculate_cosine_similarity_user_restaurants(user_profile, restaurants_profiles)
    
    #get final form 
    scores = [(restaurant["rest_id"], restaurant["rest_name"], restaurant["score"]) for restaurant in restaurants_with_score]
    
    #sort and return needed amount
    return sorted(scores, key=lambda x: x[2], reverse=True)[:amount_of_results]

def get_restaurants_collaborative(city, 
                                  user_name, 
                                  similar_users_amount=5,
                                  similarity_threshold=0.2, 
                                  amount_of_results=3,):
    #get data about all reservations in given city
    reservations_data = get_reservations(city)

    #user-restaurant mapping (who was where, user is the key)
    user_restaurant_map = defaultdict(set)
    for rest_id, rest_name, user in reservations_data:
        user_restaurant_map[user].add((rest_id, rest_name))

    #get unique users and restaurants 
    unique_users = list(user_restaurant_map.keys())
    unique_restaurants = list(set(r for rs in user_restaurant_map.values() for r in rs))

    #user-restaurant matrix (every possible compination with 1 for true combination)
    user_restaurant_matrix = np.zeros((len(unique_users), len(unique_restaurants)))
    user_idx_map = {user: idx for idx, user in enumerate(unique_users)}
    restaurant_idx_map = {restaurant: idx for idx, restaurant in enumerate(unique_restaurants)}
    
    for user, restaurants in user_restaurant_map.items():
        for restaurant in restaurants:
            user_restaurant_matrix[user_idx_map[user], restaurant_idx_map[restaurant]] = 1
    
    #compute Jaccard similarity
    user_sim_matrix = 1 - squareform(pdist(user_restaurant_matrix, metric="jaccard"))
    
    #find most similar users (with thresholds and limited amount)
    if user_name in user_idx_map:
        user_idx = user_idx_map[user_name]
        sorted_users = np.argsort(user_sim_matrix[user_idx])[:-similar_users_amount-1:-1]
        similar_users = [(u,user_sim_matrix[user_idx, u]) for u in sorted_users if user_sim_matrix[user_idx, u] >= similarity_threshold and user_sim_matrix[user_idx, u]!= 1.0] #Different than 1 to exclude the user itself
    else:
        similar_users = []

    #get restaurants from similar users in the final form, score for the restaurant is the score for user similarity 
    recommended_restaurants = set()
    for similar_user, score in similar_users:
        similar_user_restaurants = user_restaurant_map[unique_users[similar_user]]
        similar_user_restaurants = [(rest_id, rest_name, score) for rest_id, rest_name in similar_user_restaurants]
        recommended_restaurants.update(similar_user_restaurants)
    recommended_restaurants = list(recommended_restaurants)

    #sort and return needed amount
    return sorted(recommended_restaurants, key=lambda x: x[2], reverse=True)[:amount_of_results]


def get_combined_recommendations(city, 
                                 cuisine_preferences, 
                                 user_name = "", 
                                 optional_filters={},
                                 amount_of_results=3):
    #get content based recommendations
    content_based = get_restaurants_content_based(city=city, 
                                                  cuisine_preferences=cuisine_preferences, 
                                                  optional_filters=optional_filters)

    #if user_name is given use also collaborative filtering
    if user_name != "":
        collaborative = get_restaurants_collaborative(city=city, 
                                                      user_name=user_name)

        # if user is new prioritize content-based filtering
        if user_name in [user[0] for user in get_distinct_users_in_city(city)]:
            weight_cb, weight_cf = 0.5, 0.5  
        else:
            weight_cb, weight_cf = 0.8, 0.2  
        
        #recalculate the scores to reflect priority
        combined_scores = defaultdict(float)
        for rest_id, rest_name, score in content_based:
            combined_scores[(rest_id, rest_name)] = score * weight_cb
        
        for rest_id, rest_name, score in collaborative:
            if (rest_id, rest_name) in combined_scores.keys():
                combined_scores[(rest_id, rest_name)] = 1.0 #If optioned returned from both it should be good
            else:
                combined_scores[(rest_id, rest_name)] = score * weight_cf

        #sort and pepare final form
        sorted_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_recommendations = [(r[0][0], r[0][1], r[1]) for r in sorted_recommendations]

    #if user_name is NOT given use only content-based (which is already sorted)
    else:
        sorted_recommendations = content_based

    #return needed amount 
    return sorted_recommendations[:amount_of_results]

# Example test cases
if __name__ == "__main__":
    print(get_restaurants_content_based("Gdynia", "Mexican", {"avg_rating": 4.23, "price_level": 2}))
    print(get_restaurants_collaborative("Gdynia", "Monica Geller"))
    print(get_combined_recommendations("Gdynia",  "Mexican", "Monica Geller", {"avg_rating": 4.23, "price_level": 2}))
