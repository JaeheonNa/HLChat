from typing_extensions import override

from pymongo import MongoClient

from database.databaseInterface import DatabaseInterface


class MongoDBClient(DatabaseInterface):
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 27018,
                 directConnection: bool = True):
        self.mongo_client = MongoClient(
            host=host,
            port=port,
            directConnection=directConnection
        )

    @override
    def get_client(self):
        return self.mongo_client