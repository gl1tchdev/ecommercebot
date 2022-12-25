from classes.Singleton import Singleton
from classes.FieldType import FieldType
from managers.SheetDataValidationManager import SheetManager
from managers.PhotoManager import PhotoManager


class Validator(Singleton):
    body = []
    message = ''
    result = True
    kwargs = {}

    manager = SheetManager()
    ph = PhotoManager()

    def get_manager(self):
        return self.manager

    def is_ready(self):
        counter = 0
        for item in self.body:
            if item:
                counter += 1
        if counter == 0:
            return False
        if self.body[0] and counter == 1:
            return False
        if counter > 1:
            return True

    def set_body(self, array):
        self.body = array

    def set_kwargs(self, **kwargs):
        self.kwargs = kwargs

    def get_message(self):
        self.message = self.message[:-2]
        return self.message

    def get_result(self):
        return self.result

    def get_body(self):
        return self.body

    def failure(self, message):
        self.result = False
        self.message += message + '; '

    def wipe(self):
        self.result = True
        self.body = []
        self.message = ''
        self.kwargs = {}

    def process(self):
        validation_fields = self.manager.get_fields(**self.kwargs)
        if len(self.body) != len(validation_fields):
            self.failure('Нет требуемого количества полей')
            return
        for i in range(len(self.body)):
            fields = validation_fields[i]
            elem = self.body[i]
            required = fields['required']
            if (fields['_name'] == 'strength') and not (elem in ['hard', 'medium']):
                self.failure('В поле крепость может быть только hard/medium')
            if required and len(elem) == 0:
                self.failure('Поле "%s" обязательно к указанию' % fields['field_name'])
            fieldtype = fields['type']
            if fieldtype == FieldType.digit:
                if not elem.isdigit():
                    self.failure('Поле "%s" должно быть положительным числом' % fields['field_name'])
                else:
                    self.body[i] = int(elem)
            elif fieldtype == FieldType.url:
                if not self.ph.is_img_valid(elem):
                    self.failure('Ссылка на изображение некорректна')
            else:
                continue
        if self.get_result() and not self.message:
            self.message = 'OK'
