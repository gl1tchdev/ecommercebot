import httplib2
import apiclient.discovery
import os
from oauth2client.service_account import ServiceAccountCredentials
from classes.Singleton import Singleton
import config

class GoogleClient(Singleton):
    def __init__(self):
        temp = os.path.dirname(__file__).replace('clients', '')
        self.spreadsheet_id = config.spreadsheet_id
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            temp + 'credentials.json',
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    def get(self, ranges):
        data = self.service.spreadsheets().values().batchGet(
            spreadsheetId=self.spreadsheet_id,
            ranges=ranges,
            majorDimension='COLUMNS'
        ).execute()
        return data.get('valueRanges')

    def write_batch(self, sheet, range, list):
        resource = {
            "majorDimension": "COLUMNS",
            "values": [list]
        }
        return self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=sheet + '!' + range,
            valueInputOption='RAW',
            body=resource
        ).execute()

    def send_response(self, sheet, index, res):
        resource = {
            "majorDimension": "ROWS",
            "values": [[res]]
        }
        return self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=sheet + '!' + 'L%i' % (index + 3),
            valueInputOption='RAW',
            body=resource
        ).execute()