from classes.Singleton import Singleton
from data.Sheets import SHEETS


class SheetManager(Singleton):
    SHEETS = SHEETS

    def find_sheet(self, **kwargs):
        kwargs_keys = kwargs.keys()
        sheet_keys = self.SHEETS[0].keys()
        for kwargs_key in kwargs_keys:
            if not kwargs_key in sheet_keys:
                return None
        for sheet in self.SHEETS:
            for key in sheet:
                for kwargs_key in kwargs_keys:
                    if sheet[key] == kwargs[kwargs_key]:
                        return sheet

    def get_service_name_by_sheet_name(self, sheet_name):
        return self.find_sheet(sheet_name=sheet_name)['_name']

    def get_sheet_name_by_service_name(self, service_name):
        return self.find_sheet(_name=service_name)['sheet_name']

    def get_fields(self, **kwargs):
        return self.find_sheet(**kwargs)['fields']

    def get_location(self, **kwargs):
        return self.find_sheet(**kwargs)['location']

    def get_list_of_sheets(self):
        sheets_names = []
        for sheet in self.SHEETS:
            sheets_names.append(sheet['sheet_name'])
        return sheets_names

    def get_list_of_service_field_names(self, **kwargs):
        names = []
        fields = self.get_fields(**kwargs)
        for field in fields:
            names.append(field['_name'])
        return names


    def get_transformed_location(self, **kwargs):
        sheet = self.find_sheet(**kwargs)
        sheet_name = sheet['sheet_name']
        location = sheet['location']
        result = []
        for item in location:
            result.append('%s!%s3:%s' % (sheet_name, item, item))
        return result

    def compile2table(self, google_data):
        count_columns = len(google_data)
        biggest_length = 0
        table = []

        for column in google_data:
            values = column.get('values')
            if values is None:
                length = 0
            else:
                length = len(values[0])
            if biggest_length < length:
                biggest_length = length

        for item in google_data:
            values = item.get('values')
            if values is None:
                values = []
                for i in range(biggest_length):
                    values.append('')
                item.update({'values': [values]})
        for i in range(biggest_length):
            row = []
            for k in range(count_columns):
                value = ''
                try:
                    value = google_data[k]['values'][0][i]
                except IndexError:
                    value = ''
                row.append(value)
            table.append(row)
        return table