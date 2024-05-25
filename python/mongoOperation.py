
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
    
    def initDevice(self, deviceid):
        res = self.myCol.find_one({'device': deviceid})
        if res:
            return None
        else:
            res = self.myCol.insert_one({'device': deviceid, 'client': 0})
    
    def assignDevice(self, deviceid: int, doctorid: int):
        filter = {'_id': doctorid}
        update = {'$set': {f'devices.{deviceid}': 0}}
        res = self.myCol.find_one_and_update(filter, update)
        return res
    
    def assignUser(self, doctorid: int, clientid: int, deviceid: int):
        filter = {'_id': doctorid}
        
        try:
            res=self.myCol.find_one(filter)
            if res:
                if(len(res['devices'])>1):
                    for key,val in res['devices'].items():
                        if val==clientid:
                            update = {'$set': {f'devices.{key}': 0}}
                            res =self.myCol.find_one_and_update(
                                filter, update)
                            break
        except Exception as e:
            print(e)
        update = {'$set': {f'devices.{deviceid}': clientid}}
        res = self.myCol.find_one_and_update(filter, update)
        return res

    def assignConnection(self, deviceid: int, clientid: int):
        filter={'client':clientid}
        update={'$set':{'client':0}}
        try:
            res=self.myCol.find_one_and_update(filter,update)
        except Exception as e:
            pass
        filter = {'device': deviceid}
        update = {'$set': {'client': clientid}}
        res = self.myCol.find_one_and_update(filter, update)
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

    
    # def updateDevice(Self,deviceid,clientid):
    #     filter={'client':clientid}
    #     update={'device':deviceid}
    #     res=Self.myCol.find_one_and_update(filter,update)
    

    

    def getClientID(self, deviceid):
        res = self.myCol.find_one({'device': deviceid})
        if res:
            return res['client']
        return res
    