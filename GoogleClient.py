import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

class GoogleClient:
    def __init__(self):
        self.spreadsheet_id = '1Zr1MbTxQEueIj0MWLqrR1LEBgI1soYEzhbZ0ChWJ28Y'
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json',
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

    SHEETS = {
        'manufacturers': 'Производители',
        'models': 'Модели',
        'cartridges': 'Картриджи',
        'evoparators': 'Испарители',
        'liquids': 'Жидкости',
        'other': 'Прочее'
    }

    def get(self, sheet, range):
        return self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=sheet + '!' + range,
            majorDimension='ROWS'
        ).execute()

    def send_response(self, sheet, res):
        data = self.get(sheet, 'L3:L')
        if not data.get('values'):
            answer_point = 'L3'
        else:
            answer_point = 'L' + str(3 + len(data['values']))
        resource = {
            "majorDimension": "ROWS",
            "values": res
        }
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=sheet + '!' + answer_point,
            body=resource,
            insertDataOption="OVERWRITE",
            valueInputOption="USER_ENTERED"
        ).execute()

