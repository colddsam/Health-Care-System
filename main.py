from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os
import random
from python.sheetOperation import GspreadConnection
from python.smtpOperation import SMTPserver
from python.mongoOperation import MongoConnection
from python.mlModels import mlModel
import secret as sc

load_dotenv()

temp=100
MODELPATH=sc.MODELPATH
MONGOUSERNAME = sc.MONGOUSERNAME
MONGOPASSWORD = sc.MONGOPASSWORD
SMTP_USERNAME = sc.EMAIL_ID
SMTP_PASSWORD = sc.PASSWORD
SERVICE_ACCOUNT_FILE = sc.SERVICE_ACCOUNT_FILE
SCOPES = ['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive']
ClientID:int

app = FastAPI()
smtp = SMTPserver(SMTP_USERNAME=SMTP_USERNAME, SMTP_PASSWORD=SMTP_PASSWORD)
gspread = GspreadConnection(
    SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE, SCOPES=SCOPES)
mongo = MongoConnection(username=MONGOUSERNAME, password=MONGOPASSWORD)
getClientID=MongoConnection(username=MONGOUSERNAME,password=MONGOPASSWORD,collectionName='device data')
ml=mlModel(model_path=MODELPATH)

class User(BaseModel):
    name: str
    email: str
    phNo: int
    age: int
    bloodGroup: str


class Data(BaseModel):
    heart_rate: float
    spo2: float
    temperature: float
    ECGSignal:float

class Device(BaseModel):
    value: float
    id: str
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return 'This is ESP 8266 backend fetch API'

@app.post('/assign/')
async def assign(deviceid:int,clientid:int):
    try:
        res=getClientID.assignDevice(deviceid=deviceid,clientid=clientid)
        return {"report":"positive","response":res}
    except Exception as e:
        return {"report":"negative","response":e}

@app.post('/append/')
async def append(_id: int, data: Data):
    try:
        data_dict = data.model_dump()
        clientid = getClientID.getClientID(deviceid=_id)
        stressLevel = ml.stressCalculation([data_dict['heart_rate']])
        value = [datetime.now().strftime(
            "%m/%d/%Y, %H:%M:%S"), data_dict['spo2'], data_dict['temperature'], data_dict['heart_rate'], data_dict['ECGSignal'],stressLevel]
        res = gspread.appendData(_id=str(clientid), data=value)
        return {"report": res}
    except Exception as e:
        return {"report": "negative", "error": str(e)}


@app.post('/adduser/')
async def addUser(user: User):
    data = user.model_dump()
    data['_id'] = random.randint(100000, 999999)
    try:
        smtp.sendID(value=data['_id'], receiver_email=data['email'])
        mongo.createData(data=data)
        gspread.addWorksheet(_id=str(data['_id']))
        return {"report": 'positive', 'message': 'operation successful'}
    except Exception as e:
        return {"report": "negative", "error": str(e)}


@app.get("/show/")
async def show(_id: str):
    try:
        res = gspread.showData(_id=str(_id))
        return res
    except Exception as e:
        return {"report": "negative", "error": str(e)}
    
@app.get("/find/")
async def find(_id:str):
    try:
        res=mongo.find(_id=int(_id))
        return res
    except Exception as e:
        return {"report": "negative", "error": str(e)}


@app.post("/sendmail/")
async def mail(device:Device):
    data=device.model_dump()
    _id=data['id']
    value=data['value']
    _id=int(_id)
    if _id:
        res=getClientID.getClientID(deviceid=_id)
        user_det=mongo.find(_id=int(res))
        email=user_det['email']
        try:
            res = smtp.sendAlert(value=value, receiver_email=email)
            return res
        except Exception as e:
            return {"report": "negative", "error": e}
    return {"report":"negative","error":"id not assigned"}

@app.get("/data/")
async def getData(_id:int):
    try:
        clientid = getClientID.getClientID(deviceid=_id)
        data=gspread.lastData(str(clientid))
        return data
    except Exception as e:
        return {"report": "negative", "error": str(e)}

@app.get("/test/")
async def getTime():
    try:
        return datetime.now().strftime(
            "%m/%d/%Y, %H:%M:%S")
    except Exception as e:
        return {"report": "negative", "error": str(e)}
