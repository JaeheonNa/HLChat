from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from config import mongo_host, mongo_port, mongo_db_name

class MongoDB():
    def __init__(self):
        self.client = None
        self.engine = None

    def connect(self):
        self.client = AsyncIOMotorClient(mongo_host, port=mongo_port)
        self.engine = AIOEngine(client=self.client, database=mongo_db_name)

    def disconnect(self):
        self.client.close()

    def getEngine(self):
        return self.engine

mongodb = MongoDB()

def getMonoDB():
    return mongodb