from dotenv import load_dotenv
from pymongo import MongoClient

import src.mongo 


def main():
    load_dotenv()
    client = MongoClient('localhost', 27017)
    db = client.companies
    src.mongo.filter_companies(db, 'companies', 'results')
    punctuation = src.mongo.get_punctuation(db, 'results', src.mongo.get_city(db, 'results'))
    print(src.mongo.find_the_right_location(punctuation))

if __name__ == '__main__':
    main()