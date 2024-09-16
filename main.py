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
from python.clipText import gretingSystem, alertText
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
getPatient = MongoConnection(username=MONGOUSERNAME, password=MONGOPASSWORD)
getDevice=MongoConnection(username=MONGOUSERNAME,password=MONGOPASSWORD,collectionName='device data')
getDoctor=MongoConnection(username=MONGOUSERNAME,password=MONGOPASSWORD,collectionName='doctors data')
ml=mlModel(model_path=MODELPATH)

class User(BaseModel):
    name: str
    email: str
    password:str
    phNo: int
    age: int
    bloodGroup: str
    gender:str


class Doctor(BaseModel):
    registration:int
    name: str
    email: str
    password: str
    phNo: int
    age: int
    bloodGroup: str
    gender: str

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
    return 'This is Health Mate backend fetch API'

@app.post('/assign/')
async def assign(deviceid: int, doctorid: int):
    try:
        res=getDevice.initDevice(deviceid=deviceid)
        clientid=0
        if(res):
            clientid=res["client"]
            
        res=getDoctor.assignDevice(deviceid=deviceid,doctorid=doctorid,clientid=clientid)
        return {"report": "positive", "response": res}
    except Exception as e:
        return {"report":"negative","response":e}

@app.post('/patient/')
async def assignPatient(doctorid:int,patientid:int,deviceid:int):
    try:
        res=getDevice.assignConnection(deviceid=deviceid,clientid=patientid)
        res=getDoctor.assignUser(doctorid=doctorid,clientid=patientid,deviceid=deviceid)    
        return {"report": "positive", "response": res}
    except Exception as e:
        return {"report": "negative", "response": e}

@app.post('/append/')
async def append(_id: int, data: Data):
    try:
        data_dict = data.model_dump()
        clientid = getDevice.getClientID(deviceid=_id)
        stressLevel = ml.stressCalculation([data_dict['heart_rate']])
        if(data_dict['spo2']<=0):
            data_dict["spo2"]=-1
        if((data_dict['heart_rate']>=200)or(data_dict['heart_rate']<=40)):
            data_dict['heart_rate']=-1
            stressLevel=-1
        if(data_dict["temperature"]<=0):
            data_dict['temperature']=-1
        value = [datetime.now().strftime(
            "%m/%d/%Y, %H:%M:%S"), data_dict['spo2'], data_dict['temperature'], data_dict['heart_rate'], data_dict['ECGSignal'],stressLevel]
        res = gspread.appendData(_id=str(clientid), data=value)
        return {"report": res}
    except Exception as e:
        return {"report": "negative", "error": str(e)}


@app.post('/adduser/')
async def addUser(user: User):
    data = user.model_dump()
    res = getPatient.findUserId(email=data['email'], password=data["password"])
    if(res):
        return None
    else:
        data['_id'] = random.randint(100000, 999999)
        try:
            smtp.sendID(gretingSystem=gretingSystem(value=data["_id"]), receiver_email=data['email'])
            getPatient.createData(data=data)
            gspread.addWorksheet(_id=str(data['_id']))
            return {"report": 'positive', 'message': 'operation successful'}
        except Exception as e:
            return {"report": "negative", "error": str(e)}
        

@app.post('/adddoctor/')
async def addDoctor(user: Doctor):
    data = user.model_dump()
    res = getDoctor.findUserId(email=data['email'], password=data["password"])
    if (res):
        return None
    else:
        data['_id'] = random.randint(100000, 999999)
        data["devices"]={}
        try:
            smtp.sendID(gretingSystem=gretingSystem(
                value=data["_id"]), receiver_email=data['email'])
            res=getDoctor.createData(data=data)
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
        res=getPatient.find(_id=int(_id))
        return res
    except Exception as e:
        return {"report": "negative", "error": str(e)}
    
@app.get("/getdoctor/")
async def find(_id:str):
    try:
        res=getDoctor.find(_id=int(_id))
        return res
    except Exception as e:
        return {"report": "negative", "error": str(e)}


@app.get("/finduser/")
async def findUserId(email: str,password:str):
    try:
        res = getPatient.findUserId(email=email, password=password)
        return res
    except Exception as e:
        return {"report": "negative", "error": str(e)}
    

@app.get("/finddoctor/")
async def findUserId(email: str,password:str):
    try:
        res = getDoctor.findUserId(email=email, password=password)
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
        res=getDevice.getClientID(deviceid=_id)
        user_det=getPatient.find(_id=int(res))
        email=user_det['email']
        try:
            res = smtp.sendAlert(alertText=alertText(value=value), receiver_email=email)
            return res
        except Exception as e:
            return {"report": "negative", "error": e}
    return {"report":"negative","error":"id not assigned"}

@app.get("/data/")
async def getData(_id:int):
    try:
        clientid = getDevice.getClientID(deviceid=_id)
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
