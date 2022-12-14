import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from classes.Singleton import Singleton

class GoogleClient(Singleton):
    def __init__(self):
        self.spreadsheet_id = '1Zr1MbTxQEueIj0MWLqrR1LEBgI1soYEzhbZ0ChWJ28Y'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json',
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