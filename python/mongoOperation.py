
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import random

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

    def findUserId(self, email:str,password:str|None=None):
        if(password):
            res = self.myCol.find_one({'email': email, 'password':password})
        else:
            res = self.myCol.find_one({'email': email})
        if res:
            return res['_id']
        else:
            return None

    def assignDevice(self, deviceid, clientid):
        filter = {'deviceid': deviceid}
        update = {'$set': {'clientid': clientid}}
        res = self.myCol.find_one_and_update(filter, update)
        if not res:
            _id=random.randint(100000, 999999)
            res = self.myCol.insert_one({'_id':_id,'deviceid': deviceid, 'clientid': clientid})
        return 'successfully appended'

    def getClientID(self, deviceid):
        res = self.myCol.find_one({'deviceid': deviceid})
        if res:
            return res['clientid']
        return res
    