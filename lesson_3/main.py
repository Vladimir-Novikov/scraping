from pymongo import MongoClient
from pprint import pprint
from pymongo.errors import DuplicateKeyError as dke

client = MongoClient('localhost', 27017)

db = client['users1502']    # database
persons = db.persons        # collection
books = db.books            # collection

# try:
#     persons.insert_one({"_id": 564843135186,
#                         "author": "Peter2",
#                         "age": 38,
#                         "text": "is cool! Wildberry",
#                         "tags": ['cool', 'hot', 'ice'],
#                         "date": '14.06.1983'})
# except dke:
#     print('Duplicate key error collection')

# persons.insert_many([{"author": "John",                               # Р”РѕР±Р°РІР»СЏРµРј РЅРµСЃРєРѕР»СЊРєРѕ РґРѕРєСѓРјРµРЅС‚РѕРІ РІ Р±Р°Р·Сѓ
#                "age" : 29,
#                "text": "Too bad! Strawberry",
#                "tags": 'ice',
#                "date": '04.08.1971'},
#
#                     {"_id": 123,
#                         "author": "Anna",
#                "age" : 36,
#                "title": "Hot Cool!!!",
#                "text": "easy too!",
#                "date": '26.01.1995'},
#
#                    {"author": "Jane",
#                "age" : 43,
#                "title": "Nice book",
#                "text": "Pretty text not long",
#                "date": '08.08.1975',
#                "tags":['fantastic', 'criminal']}])


# for doc in persons.find({'author': 'Peter2'}):
#     pprint(doc)

# for doc in persons.find({'author': 'Peter2', '_id': 564843135186}):
#     pprint(doc)

# for doc in persons.find({'$or': [{'author': 'Peter2'}, {'age': 43}]}):
#     pprint(doc)

# for doc in persons.find({'age': {'$lte': 35}}):
#      pprint(doc)

# for doc in persons.find({'$or': [{'author': 'Peter2'}, {'age': {'$lte': 35}}]}):
#     pprint(doc)

# for doc in persons.find({'author': {'$regex': 'J'}}):
#     pprint(doc)

# result = persons.find_one({'author': 'Peter2'})
# if result:
#     print('Found')
#     print(result)
# else:
#     print('Not Found')

new_data = {
    "author": "Andrey",
               "age" : 28,
               "text": "is hot!",
               "date": '11.09.1991'}


# persons.update_one({'author': 'Peter2'}, {'$set': new_data})
# persons.replace_one({'author': 'Andrey'}, new_data)

# persons.delete_one({'author': 'Peter2'})
result = persons.delete_one({})


# result = list(persons.find({'author': 'Peter2'}))
# pprint(result)

for doc in persons.find({}):
    pprint(doc)