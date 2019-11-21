import operator
from pymongo import MongoClient, GEOSPHERE
import pandas as pd
from bson import SON

import yelp


# with these lines of code you can:
# 0) generate a new collection using Crunchbase Mongodb and based on this new collection:
# 1) find out which is the best city where to locate your company
# 2) get the information extracted from yelp for Starbucks, airports and vegan restaurants 
# 3) weights potencial offices to place your company based on Starbucks at 500 meters, restaurants 1 km, airports 30 km
# 4) assigns 1 to offices which satisfy every criteria so 1 for restaurant , 1 for Starbucks
# 5) sums the total amount of points for each office 
# 6) avoids a 'tie' situation by sorting the database by which company has most employees
# 7) returns a location based on the winner


def filter_companies(db, collection, new_collection):
    '''creates new collection based on criteria and also the 2dsphere Indexes for offices locations'''
    
    db[collection].aggregate([
        {'$unwind': '$funding_rounds'},
        {'$group': {
            '_id': '$_id',
            'name': {'$first': '$name'},
            'deadpooled_year': {'$first': '$deadpooled_year'},
            'founded_year': {'$first': '$founded_year'},
            'number_of_employees': {'$first': '$number_of_employees'},
            'offices': {'$first': '$offices'},
            'funding_sum': {'$sum': '$funding_rounds.raised_amount'}
        }},
        {'$match': {'$and': [
            {'deadpooled_year': None},
            {'funding_sum': {'$gt': 1000000}},
            {'founded_year': {'$gte': 2000}},
            {'number_of_employees': {'$gte': 50}}
        ]}},
        {'$unwind': '$offices'},
        {'$match': {'offices.latitude': {'$ne': None}}},
        {'$addFields': {
            'city': '$offices.city',
            'loc': {
                'type': 'Point',
                'coordinates': ['$offices.longitude', '$offices.latitude']
            }
        }},
        {'$project': {
            '_id': 0,
            'name': '$name',
            'funding_rounds': '$funding_rounds',
            'number_of_employees': '$number_of_employees',
            'funding_sum': '$funding_sum',
            'city': '$city',
            'loc': '$loc'
        }},
        {'$sort': {'number_of_employees': 1}},
        {'$out': new_collection}
    ])
    db[new_collection].create_index([("loc", GEOSPHERE)])


def get_city(db, collection):
    aggregation = db[collection].aggregate([
        {'$group': {'_id': '$city', 'count': {'$sum': 1}}}
    ])
    result = {value['_id']: value['count'] for value in aggregation}
    return max(result.items(), key=operator.itemgetter(1))[0]


def get_punctuation(db, collection, city):
    df = pd.DataFrame(
        [[d['name'], d['number_of_employees'], d['loc']] for d in db[collection].find({'city': city})],
        columns=['name', 'employees', 'loc']
    )
    distances = {
        'airports': 30000,
        'restaurants': 1000,
        'starbucks': 500
    }
    data = {
        'airports': yelp.get_airports(city),
        'restaurants': yelp.get_vegan_restaurants(city),
        'starbucks': yelp.get_starbucks(city)
    }
    for kind, listing in data.items():
        df[kind] = 0
        for element in listing:
            results = db[collection].find(
                {'loc': {'$near': SON([
                    ('$geometry', SON([
                        ('type', 'Point'),
                        ('coordinates', [
                            element['coordinates']['longitude'],
                            element['coordinates']['latitude']
                        ])
                    ])),
                    ('$maxDistance', distances[kind])])}}
            )
            for r in results:
                df.at[df.loc[df['name'] == r['name']].index, kind] = 1
    df = df.astype({'airports': 'int32', 'starbucks': 'int32', 'restaurants': 'int32'})
    df['total'] = df.iloc[:, -3:-1].sum(axis=1)
    return df
    
    
def find_the_right_location(df):   
    for i in [3, 2, 1, 0]:
        df_total = df[df['total'] == i]
        if len(df_total) != 0:
            punctuation = df_total.sort_values('employees', ascending=False)
            return [punctuation.iat[0, 0], [punctuation.iat[0, 2]['coordinates'][1], punctuation.iat[0, 2]['coordinates'][0]]]

