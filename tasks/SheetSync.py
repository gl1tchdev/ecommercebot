from classes.SheetDataValidator import Validator
from clients.GoogleClient import GoogleClient
from managers.DbUploadManager import UploadManager
from managers.PhotoManager import PhotoManager
from tasks import ImgDownload

def sync():
    validator = Validator()
    validation_manager = validator.get_manager()
    service = GoogleClient()
    mc = UploadManager()
    ph = PhotoManager()

    sheets = validation_manager.get_list_of_sheets()
    for sheet in sheets:
        sheet_service_name = validation_manager.get_service_name_by_sheet_name(sheet)
        ranges = validation_manager.get_transformed_location(sheet_name=sheet)
        google_data = service.get(ranges)
        table = validation_manager.compile2table(google_data)
        empty = []
        for i in range(len(table)):
            empty.append(' ')
        service.write_batch(sheet, 'L3:L', empty)
        response = {}
        validated = []

        for i in range(len(table)):
            validator.set_body(table[i])
            validator.set_kwargs(sheet_name=sheet)
            if not validator.is_ready():
                continue
            validator.process()
            if validator.get_result():
                validated.append([i, validator.get_body()])
            else:
                response.update({i: validator.get_message()})
            validator.wipe()

        for valid in validated:
            temp = []
            for valid in validated:
                temp.append(valid[1])
            temp.pop(validated.index(valid))
            if valid[1] in temp:
                response.update({valid[0]: "Нельзя загружать в базу данных записи с одинаковым ID. Смените ID"})
                validated.pop(validated.index(valid))

        batch = []
        for valid in validated:
            service_field_names = validation_manager.get_list_of_service_field_names(sheet_name=sheet)
            split_data = mc.split_data(service_field_names, valid[1])
            db_batch = mc.search_in_db(sheet_service_name, split_data)
            if len(db_batch) == 0:
                response.update({valid[0]: "Будет загружено в базу данных"})
                batch.append(split_data)
            elif len(db_batch) == 1:
                if split_data == db_batch[0]:
                    response.update({valid[0]: "Запись есть в базе данных"})
                    batch.append(split_data)
                else:
                    response.update({valid[0]: "Запись с таким ID уже есть в базе, и обновится при следующей проверке"})
        if len(response) > 0:
            update = []
            for i in range(len(table)):
                if i in response.keys():
                    update.append(response[i])
                else:
                    update.append('')
            service.write_batch(sheet, 'L3:L%i' % (3+len(table)), update)

        deploy = mc.get_difference_to_deploy(sheet_service_name, batch)
        delete = mc.get_difference_to_delete(sheet_service_name, batch)
        if len(deploy) > 0:
            for elem in deploy:
                mc.upload(sheet_service_name, elem)

        if len(delete) > 0:
           for elem in delete:
                id = mc.get_client().find(sheet_service_name, elem, True)[0]['_id']
                mc.delete(sheet_service_name, elem)
                if elem.get('url'):
                    ph.delete_photo(elem['url'])
                mc.delete('comments', {'doc_id': str(id)})


    ImgDownload.download()
