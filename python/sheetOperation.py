import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


class GspreadConnection:
    def __init__(self, SCOPES, SERVICE_ACCOUNT_FILE) -> None:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, SCOPES)
        client = gspread.authorize(creds)
        self.sheet = client.open('sensor new data')

    def addWorksheet(self, title: str):
        worksheet = self.sheet.add_worksheet(title=title, rows=10000, cols=4)
        data = ['Date Time', 'Blood Oxygen', 'Temperature', 'Heart Rate']
        worksheet.append_row(data)
        return worksheet

    def appendData(self, title: str, data: list):
        sheet_instance = self.sheet.worksheet(title)
        return sheet_instance.append_row(data)

    def showData(self, title: str):
        sheet_instance = self.sheet.worksheet(title)
        data = pd.DataFrame(sheet_instance.get_all_values())
        return data


