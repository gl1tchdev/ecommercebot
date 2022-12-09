from classes.SheetDataValidator import Validator
from clients.GoogleClient import GoogleClient
from managers.DbUploadManager import UploadManager
from pprint import pprint

validator = Validator()
validation_manager = validator.get_manager()
service = GoogleClient()
mc = UploadManager()


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
       batch.append(validator.get_body())
    else:
        failures.append([elem, validator.get_message()])
    validator.wipe()

for elem in batch:
    mc.set_body(validation_manager.get_list_of_service_field_names(sheet_name=sheet), elem)
    mc.set_collection(validation_manager.get_service_name_by_sheet_name(sheet))
    pprint(mc.is_unique())
    #pprint(mc.upload())
    mc.wipe()