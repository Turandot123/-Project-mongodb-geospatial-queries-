import operator
from pymongo import MongoClient, GEOSPHERE
import pandas as pd
from bson import SON

import yelp

def filter_companies(db, collection, new_collection):
    db[new_collection].drop()
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
            {'funding_sum': {'$gt': 1_000_000}},
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
        'airports': 30_000,
        'restaurants': 1_000,
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
            return df_total.sort_values('employees', ascending=False).iat[0, 2]['coordinates']