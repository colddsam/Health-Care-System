from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from python.sheetOperation import GspreadConnection
from datetime import datetime
import secret as sc

SERVICE_ACCOUNT_FILE = sc.SERVICE_ACCOUNT_FILE
SCOPES = sc.SCOPES

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gspread=GspreadConnection(SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE,SCOPES=SCOPES)

@app.get('/')
def root():
    return 'This is ESP 8266 backend fetch API'

@app.post('/append/')
async def append(title:str,heart_rate:float,spo2:float,temperature:float):
    try:
        value = [datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), heart_rate,spo2,temperature]
        res = gspread.appendData(title=title,data=value)
        return {"report": res}
    except Exception as e:
        return {"report": "negative", "error": str(e)}
    
@app.post('/addsheet/')
async def addSheet(title:str):
    try:
        res = gspread.addWorksheet(title=title)
        return {"report": res}
    except Exception as e:
        return {"report": "negative", "error": str(e)}

@app.get("/show/")
async def show(title:str):
    try:
        res = gspread.showData(title=title)
        return res
    except Exception as e:
        return {"report": "negative", "error": str(e)}
