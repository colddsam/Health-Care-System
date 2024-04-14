
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoConnection:
    def __init__(self, username, password, databaseName='HealthCare', collectionName='profile data') -> None:
        uri = f"mongodb+srv://{username}:{password}@healthcare.emzypae.mongodb.net/?retryWrites=true&w=majority&appName=HealthCare"
        client = MongoClient(uri, server_api=ServerApi('1'))
        myDb = client[databaseName]
        self.myCol = myDb[collectionName]

    def createData(self, data):
        res = self.myCol.insert_one(data)
        return res

    def find(self, _id):
        res = self.myCol.find_one({'_id': _id})
        return res
