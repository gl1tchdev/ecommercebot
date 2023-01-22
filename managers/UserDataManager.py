from classes.Singleton import Singleton
from clients.MongoClient import monclient
from classes.UserRole import UserRole
import time
from copy import deepcopy

class UserDataManager(Singleton):
    mc = monclient()
    _structure = {
        'user': ['nickname', 'chat_id', 'registration_time', 'last_online', 'menu_id', 'card_id', 'role'],
        'sent_messages': ['chat_id', 'message_id']
    }
    def get_structure(self):
        return deepcopy(self._structure)

    def get_time(self):
        return time.strftime("%d/%m/%y %H:%M")

    def register_user(self, nickname, chat_id, menu_id=0, role=UserRole.STAFF):
        structure = self.get_structure()['user']
        t = self.get_time()
        return self.mc.add('user', {
            structure[0]: nickname,
            structure[1]: chat_id,
            structure[2]: t,
            structure[3]: t,
            structure[4]: menu_id,
            structure[5]: 0,
            structure[6]: role.value
        })

    def save_message(self, chat_id, message_id):
        structure = self.get_structure()['sent_messages']
        return self.mc.add('sent_messages', {
            structure[0]: chat_id,
            structure[1]: message_id
        })

    def delete_message(self, message_id):
        return self.mc.delete('sent_messages', {'message_id': message_id})

    def get_menu_id(self, nickname):
        result = self.mc.find('user', {'nickname': nickname})
        return result[0]['menu_id'] if len(result) > 0 else 0

    def has_card_id(self, nickname):
        result = self.mc.find('user', {'nickname': nickname})
        if len(result) == 0:
            return False
        return True if result[0]['card_id'] != 0 else False

    def set_card_id(self, nickname, card_id):
        return self.mc.update_one('user', {'nickname': nickname}, {'card_id': card_id})

    def get_card_id(self, nickname):
        result = self.mc.find('user', {'nickname': nickname})
        return result[0]['card_id']

    def set_menu_id(self, nickname, menu_id):
        return self.mc.update_one('user', {'nickname': nickname}, {'menu_id': menu_id})

    def is_registered(self, nickname):
        structure = self.get_structure()['user']
        result = self.mc.find('user', {structure[0]: nickname})
        return True if len(result) > 0 else False

    def get_user(self, nickname):
        return self.mc.find('user', {'nickname': nickname})[0]

    def get_nickname_by_message(self, message):
        nickname = ''
        try:
            nickname = message.from_user.username
        except:
            pass
        try:
            nickname = message.chat.username
        except:
            pass
        return nickname

    def add_to_whitelist(self, nickname):
        return self.mc.add('whitelist', {'nickname': nickname})

    def set_role(self, nickname, role):
        return self.mc.update_one('user', {'nickname': nickname}, {'role': role})