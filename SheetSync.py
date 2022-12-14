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

validated = []
for elem in table:
    validator.set_body(elem)
    validator.set_kwargs(sheet_name=sheet)
    if not validator.is_ready():
        continue
    validator.process()
    if validator.get_result():
        validated.append([table.index(elem), validator.get_body()])
    else:
        service.send_response(sheet, table.index(elem), validator.get_message())
    validator.wipe()

batch = []
for valid in validated:
    service_field_names = validation_manager.get_list_of_service_field_names(sheet_name=sheet)
    split_data = mc.split_data(service_field_names, valid[1])
    #TODO продумать логику проверки записи в бд
    batch.append(split_data)

deploy = mc.get_difference_to_deploy(validation_manager.get_service_name_by_sheet_name(sheet), batch)
delete = mc.get_difference_to_delete(validation_manager.get_service_name_by_sheet_name(sheet), batch)
if len(deploy) > 0:
    for elem in deploy:
        mc.upload(validation_manager.get_service_name_by_sheet_name(sheet), elem)
if len(delete) > 0:
    for elem in delete:
        mc.delete(validation_manager.get_service_name_by_sheet_name(sheet), elem)