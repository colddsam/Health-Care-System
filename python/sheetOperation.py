import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


class GspreadConnection:
    def __init__(self, SCOPES, SERVICE_ACCOUNT_FILE) -> None:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, SCOPES)
        client = gspread.authorize(creds)
        self.sheet = client.open('sensor new data')

    def addWorksheet(self, _id: str):
        worksheet = self.sheet.add_worksheet(title=_id, rows=10000, cols=4)
        data = ['Date Time', 'Blood Oxygen',
                'Temperature', 'Heart Rate', 'ECG Signal']
        worksheet.append_row(data)
        return worksheet

    def appendData(self, _id: str, data: list):
        sheet_instance = self.sheet.worksheet(_id)
        return sheet_instance.append_row(data)

    def showData(self, _id: str):
        sheet_instance = self.sheet.worksheet(_id)
        data = pd.DataFrame(sheet_instance.get_all_values())
        data = data.replace('','0')
        data=data.fillna(0)
        data.columns = ['Date Time', 'Blood Oxygen',
                        'Temperature', 'Heart Rate', 'ECG Signal']
        data=data.drop(index=0)
        convert_directory = {
            'Blood Oxygen': float,
            'Temperature': float,
            'Heart Rate': float,
            'ECG Signal':float
        }
        data = data.astype(convert_directory)
        data=data.tail(30)
        data=data.reset_index(drop=True)
        return data




