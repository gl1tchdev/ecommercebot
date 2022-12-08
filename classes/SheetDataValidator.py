from classes.Singleton import Singleton
from classes.FieldType import FieldType
from managers.SheetDataValidationManager import SheetManager
from validators import url


class Validator(Singleton):
    body = []
    message = 'OK'
    result = True
    kwargs = {}

    manager = SheetManager()

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

    def failure(self, message):
        if self.message == 'OK':
            self.message = ''
        self.result = False
        self.message += message + '; '

    def wipe(self):
        self.result = True
        self.body = []
        self.message = 'ОК' #TODO пофиксить OK вначале сообщения об ошибке
        self.kwargs = {}

    def process(self):
        # TODO: Добавить проверку на совпадение ID у элементов
        validation_fields = self.manager.get_fields(**self.kwargs)
        if len(self.body) != len(validation_fields):
            self.failure('Нет требуемого количества полей')
            return
        for i in range(len(self.body)):
            field = validation_fields[i]
            elem = self.body[i]
            required = field['required']
            if required and len(elem) == 0:
                self.failure('Поле "%s" обязательно к указанию' % field['field_name'])
            type = field['type']
            if type == FieldType.digit:
                if not elem.isdigit():
                    self.failure('Поле "%s" должно быть положительным числом' % field['field_name'])
            elif type == FieldType.url:
                if not url(elem):
                    self.failure('Поле "%s" должно быть ссылкой' % field['field_name'])
            else:
                continue