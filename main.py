from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from python.gspread import GspreadOperation
from datetime import datetime
import secret as sc
load_dotenv()

SERVICE_ACCOUNT_FILE=sc.SERVICE_ACCOUNT_FILE
SCOPES = sc.SCOPES
SPREADSHEET_ID = sc.SPREADSHEET_ID

# if __name__=='__main__':
#     gspread = GspreadOperation(
#         SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE, SCOPES=SCOPES, SPREADSHEET_ID=SPREADSHEET_ID)
#     value = [datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), 20.10,10,30]
#     res = gspread.append_data(value)
#     res = gspread.show_data()
#     print(type(res))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gspread = GspreadOperation(
    SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE,
    SCOPES=SCOPES,
    SPREADSHEET_ID=SPREADSHEET_ID
)


@app.post('/')
def rootpage():
    return 'This is ESP 8266 backend fetch API'

@app.post('/append/')
async def append(heart_rate=float,spo2=float,temperature=float):
    try:
        value = [datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), heart_rate,spo2,temperature]
        res = gspread.append_data(value)
        return {"report": res}
    except Exception as e:
        return {"report": "negative", "error": str(e)}

# @app.get("/connection/")
# async def update_content(data: float = Query(...)):
#     try:
#         value = [datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), data]
#         res = gspread.append_data(value)
#         return {"report": res}
#     except Exception as e:
#         return {"report": "negative", "error": str(e)}


@app.get("/show/")
async def show():
    res = gspread.show_data()
    return res
