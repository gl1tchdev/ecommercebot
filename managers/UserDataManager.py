from classes.Singleton import Singleton
from clients.MongoClient import monclient
from classes.UserRole import UserRole
import time
from copy import deepcopy

class UserDataManager(Singleton):
    mc = monclient()
    _structure = {
        'user': ['nickname', 'registration_time', 'last_online', 'menu', 'card', 'role'],
        'messages': ['nickname', 'chat_id', 'user_id']
    }
    def get_structure(self):
        return deepcopy(self._structure)

    def get_time(self):
        return time.strftime("%d/%m/%y %H:%M")

    def register_user(self, nickname, id=0, card=0,role=UserRole.STAFF):
        structure = self.get_structure()['user']
        return self.mc.add('user', {
            structure[0]: nickname,
            structure[1]: self.get_time(),
            structure[2]: self.get_time(),
            structure[3]: card,
            structure[4]: id,
            structure[5]: role.value
        })

    def update_online(self, nickname):
        structure = self.get_structure()['user']
        return self.mc.update_one('user',
                                  {structure[0]: nickname},
                                  {structure[2]: self.get_time()})

    def been_online(self, nickname):
        structure = self.get_structure()['user_data']
        result = self.mc.find('user', {structure[0]: nickname})
        if len(result) > 0:
            return result[structure[2]]
        else:
            return None

    def is_registered(self, nickname):
        structure = self.get_structure()['user']
        result = self.mc.find('user', {structure[0]: nickname})
        return True if len(result) > 0 else False

    def has_last_message(self, nickname):
        structure = self.get_structure()
        result = self.mc.find('user_data', {structure['user_data'][0]: nickname})
        return True if len(result) > 0 else False

    def add_data(self, nickname, id):
        structure = self.get_structure()
        self.update_online(nickname)
        return self.mc.add('user_data', {structure['user_data'][0]: nickname,
                                         structure['user_data'][1]: id})

    def get_last_message(self, nickname):
        structure = self.get_structure()
        self.update_online(nickname)
        return self.mc.find('user_data', {structure['user_data'][0]: nickname})[0][structure['user_data'][1]]

    def set_last_message(self, nickname, id):
        structure = self.get_structure()
        return self.mc.update_one('user_data', {structure['user_data'][0]: nickname}, {structure['user_data'][1]: id})

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