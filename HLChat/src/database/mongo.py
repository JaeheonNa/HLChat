from pymongo import MongoClient

mongo_client = MongoClient(
    host='127.0.0.1',
    port=27018,
    directConnection=True
)

def get_mongo_client():
    return mongo_client