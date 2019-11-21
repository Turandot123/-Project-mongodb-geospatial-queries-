from dotenv import load_dotenv
from pymongo import MongoClient

import mongo 


def main():
    load_dotenv()
    client = MongoClient('localhost', 27017)
    db = client.companies
    mongo.filter_companies(db, 'companies', 'results')
    punctuation = mongo.get_punctuation(db, 'results', mongo.get_city(db, 'results'))
    print(mongo.find_the_right_location(punctuation))

if __name__ == '__main__':
    main()