**Preparation**
- Generate api key for Google API - as described in https://developers.google.com/maps/get-started#api-key
- Store generated api key in a file called api_key.txt in the same folder as notebooks
- install googlemaps in your environment

**Data collection**
- run 'get_restaurants_from_city.ipynb' notebook 
    - update cities and food types variables to your needs
- run 'get_restaurants_details.ipynb'
- run 'prepare_restaurant_info.ipynb' 

**Output**
You should have a 'all_restaurants_info.csv' file with following structure:

|ID|City|Place_ID|Place_Name|Cuisine|Address|Phone Number|Price level|Avg rating|Amount of ratings|Vegetarian|Beer|Wine|Opening Hours|tags
|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----
0|Gdynia|ChIJK4PtjPun_UYRRYuECz2jxWk|10/10 Sushi|['japanese', 'sushi']|Świętojańska 48, 81-393 Gdynia, Poland|+48 534 454 824|2.0|4.4|229|False|True|False|[{'close': {'day': 0, 'time': '2100'}, 'open': {'day': 0, 'time': '1200'}}]|['meal_takeaway', 'restaurant', 'food', 'point_of_interest', 'establishment']
1|Sopot|ChIJvybH-5IK_UYRfeQa5nqUcfA|1911 Restaurant|['turkish', 'chinese']|Grunwaldzka 4/6, 81-759 Sopot, Poland|+48 572 945 145|2.0|4.7|524|True|True|True|[{'close': {'day': 0, 'time': '2100'}, 'open': {'day': 0, 'time': '1300'}}]|['restaurant', 'bar', 'food', 'point_of_interest', 'establishment']

This file can be loaded to pandas DataFrame or to database