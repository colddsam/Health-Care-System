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
import secret as sc

load_dotenv()

temp=100

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
        clientid=getClientID.getClientID(deviceid=_id)
        value = [datetime.now().strftime(
            "%m/%d/%Y, %H:%M:%S"), data_dict['spo2'], data_dict['temperature'], data_dict['heart_rate'], data_dict['ECGSignal']]
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
async def mail(value, receiveremail: str):
    try:
        res = smtp.sendAlert(value=value, receiver_email=receiveremail)
        return {"report": "positive", "message": res}
    except Exception as e:
        return {"report": "negative", "error": str(e)}
