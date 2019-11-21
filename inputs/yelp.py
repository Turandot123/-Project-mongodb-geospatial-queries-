
import os
import requests
import json
from dotenv import load_dotenv


# Ask for access to Yelp 
# Using token which is in a getenv file
def make_yelp_api_call(params):
    '''calls YELP API'''
    load_dotenv()
    api_key= os.getenv('YELP_API_KEY')
    headers = {'Authorization': f'Bearer {api_key}'}
    url = 'https://api.yelp.com/v3/businesses/search'
    req = requests.get(url, params=params, headers=headers)
    return json.loads(req.text)['businesses']

def get_airports(city):
    '''get information of airports based on a specific city'''
    airports = make_yelp_api_call({'categories':'airports','location':city})
    return [a for a in airports if a['categories'][0]['alias'] == 'airports'] 

def get_starbucks(city):
    '''get information of Starbucks based on a specific city'''
    return make_yelp_api_call({'term': 'Starbucks', 'location': city})


def get_vegan_restaurants(city):
    '''get information of restaurants based on a specific city'''
    return make_yelp_api_call({'term': 'vegan', 'location': city})




