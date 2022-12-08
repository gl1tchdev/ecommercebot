from classes.SheetDataValidator import Validator
from clients.GoogleClient import GoogleClient
from pprint import pprint

validator = Validator()
validation_manager = validator.get_manager()
service = GoogleClient()
sheet = 'Производители'
ranges = validation_manager.get_transformed_location(sheet_name=sheet)
google_data = service.get(ranges)
table = validation_manager.compile2table(google_data)
batch = []
not_ready = []
failures = []
for elem in table:
    validator.set_body(elem)
    validator.set_kwargs(sheet_name=sheet)
    if not validator.is_ready():
        not_ready.append(elem)
        continue
    validator.process()
    if validator.get_result():
       batch.append(elem)
    else:
        failures.append([elem, validator.get_message()])
    validator.wipe()

pprint('Готово к заливке: ')
pprint(batch)
pprint('Не подлежит валидации: ')
pprint(not_ready)
pprint('Не прошло валидацию: ')
pprint(failures)