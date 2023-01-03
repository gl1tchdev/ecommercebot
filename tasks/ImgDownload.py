from managers.PhotoManager import PhotoManager
from clients.MongoClient import monclient
from managers.SheetDataValidationManager import SheetManager

def download():
    ph = PhotoManager()
    mc = monclient()
    vm = SheetManager()

    sheets = vm.get_list_of_sheets()
    sheets_with_urls = []
    for sheet in sheets:
        names = vm.get_list_of_service_field_names(sheet_name=sheet)
        if 'url' in names:
            sheets_with_urls.append(vm.get_service_name_by_sheet_name(sheet))
    for sheet in sheets_with_urls:
        docs = mc.find(sheet)
        if len(docs) == 0:
            continue
        for elem in docs:
            if not elem['url']:
                continue
            fs = mc.find('photos', {'url': elem['url']})
            if len(fs) > 0:
                continue
            filename = ph.download(elem['url'])
            mc.add('photos', {'url': elem['url'], 'filename': filename})

download()