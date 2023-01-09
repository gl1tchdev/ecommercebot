from telebot import types
from classes.Singleton import Singleton
from managers.DbSearchManager import SearchManager
from managers.SheetDataValidationManager import SheetManager
from managers.HTMLManager import HTMLManager
from clients.MongoClient import monclient
import config
import time


class MessageManager(Singleton):
    hm = HTMLManager()
    vm = SheetManager()
    sm = SearchManager()
    mc = monclient()

    def is_in_whitelist(self, nickname):
        return True if nickname in config.whitelist else False

    def get_markup(self, dict):
        keyboard = self.get_keybard()
        for key in dict:
            keyboard.row(self.get_button(dict[key], key))
        return keyboard

    def create_comment(self, id, nickname, text):
        t = time.strftime("%D %H:%M")
        return self.mc.add('comments',
                           {'doc_id': id,
                            'time': t,
                            'nickname': nickname,
                            'text': text})

    def get_start(self):
        return self.get_markup(self.sm.dynamic_search('start'))

    def search(self, text):
        search = self.sm.search_by_text(text)
        if len(search) > 0:
            return self.get_markup(search).row(self.get_back_button('start'))
        else:
            return None

    def get_force_reply(self):
        return types.ForceReply(selective=False)

    def get_button(self, text, callback):
        return types.InlineKeyboardButton(text=text, callback_data=callback)

    def get_keybard(self):
        return types.InlineKeyboardMarkup()

    def get_back_button(self, backpath, need_keyboard=False):
        back_button = self.get_button('Назад', backpath)
        if need_keyboard:
            return self.get_keybard().row(back_button)
        else:
            return back_button

    def make_body(self, info):
        body = ''
        for elem in info:
            key, val = next(iter(elem.items()))
            if val == 'empty':
                continue
            body += '%s: %s' % (key, val)
            body += '\n'
        return body

    def get_info_comment(self, path):
        query = self.sm.get_query(path.split('/'))
        result = self.sm.force_search(query)
        return self.hm.spoiler(str(result['_id']))

    def process_card(self, info, call, backpath, obj, path=''):
        funcs = [obj.send_photo, obj.send_message]
        keyboard = self.get_keybard()
        keyboard.row(self.get_button('Комментировать', path + '/comment'), self.get_back_button(backpath))
        last_elem = info.pop(len(info)-1)
        first_elem = info.pop(0)
        body = self.make_body(info)
        if last_elem != 'empty':
            func = funcs[0]
        else:
            func = funcs[1]
        params = {
            'chat_id': call.message.chat.id,
            ('text' if func is funcs[1] else 'caption'): body,
            'reply_markup': keyboard
        }
        if func is funcs[0]:
            params.update({'photo': open(last_elem, 'rb')})
        return [func, params]