from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from datetime import datetime


class GspreadOperation:

    def __init__(self, SERVICE_ACCOUNT_FILE, SCOPES, SPREADSHEET_ID) -> None:
        self.SERVICE_ACCOUNT_FILE=SERVICE_ACCOUNT_FILE
        self.SCOPES=SCOPES
        self.SPREADSHEET_ID=SPREADSHEET_ID
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
            service = build("sheets", "v4", credentials=creds)
            sheet = service.spreadsheets()
            self.sheet = sheet
        except HttpError as e:
            self.sheet = None

    def append_data(self, values):
        body = {"values": [values]}
        try:
            result = (
                self.sheet.values().append(
                    spreadsheetId=self.SPREADSHEET_ID,
                    range="Sheet1",
                    body=body,
                    valueInputOption="RAW",
                ).execute()
            )
            return result
        except HttpError as err:
            return err

    def show_data(self):
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.SPREADSHEET_ID, range="Sheet1").execute()
            val = result.get("values", [])
            return val
        except HttpError as err:
            return err


# gspread = GspreadOeration()
# value = [datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), 20.10]
# res = gspread.append_data(value)
# print(res)
