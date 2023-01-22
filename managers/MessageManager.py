from telebot import types, TeleBot, apihelper
from classes.Singleton import Singleton
from managers.DbSearchManager import SearchManager
from managers.SheetDataValidationManager import SheetManager
from managers.HTMLManager import HTMLManager
from managers.UserDataManager import UserDataManager
from clients.MongoClient import monclient
import time, config


class MessageManager(Singleton):
    def __init__(self):
        self.hm = HTMLManager()
        self.vm = SheetManager()
        self.sm = SearchManager()
        self.mc = monclient()
        self.udm = UserDataManager()
        self.bot = TeleBot(config.token, parse_mode='HTML')

    def get_bot(self):
        return self.bot

    def get_backpath(self, path):
        backpathm = path.split('/')
        backpathm.pop(len(backpathm) - 1)
        return '/'.join(backpathm)

    def get_markup(self, dict):
        keyboard = self.get_keybard()
        for key in dict:
            keyboard.row(self.get_button(dict[key], key))
        return keyboard

    def create_comment(self, id, nickname, text):
        t = time.strftime("%d/%m/%Y %H:%M")
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
        if len(callback.encode('utf-8')) > 63:
            if self.mc.is_cached(callback):
                callback = 'cache:' + self.mc.get_cache(value=callback)
            else:
                callback = 'cache:' + self.mc.cache_value(callback)
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

    def get_comment_keyboard(self, path):
        keyboard = self.get_keybard()
        keyboard.row(self.get_button('Комментировать', path + '/comment'))
        return keyboard

    def get_info_comment(self, path):
        query = self.sm.get_query(path.split('/'))
        result = self.sm.force_search(query)
        return self.hm.spoiler(str(result['_id']))

    def process_card(self, info, call, path):
        funcs = [self.bot.send_photo, self.bot.send_message]
        keyboard = self.get_comment_keyboard(path)
        backpath = self.get_backpath(path)
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
            params.update({'photo': last_elem})
        nickname = self.udm.get_nickname_by_message(call.message)
        if not self.udm.has_card_id(nickname):
            self.send_card(func, nickname, call, params, backpath)
        else:
            card_id = self.udm.get_card_id(nickname)
            if func is funcs[0]:
                try:
                    with open(params['photo'], 'rb') as f:
                        self.bot.edit_message_media(media=types.InputMedia(type='photo', media=f), chat_id=params['chat_id'], message_id=card_id)
                    self.bot.edit_message_caption(body, params['chat_id'], card_id, reply_markup=keyboard)
                except apihelper.ApiTelegramException:
                    self.send_card(func, nickname, call, params, backpath, card_id)
            else:
                try:
                    self.bot.edit_message_text(body, params['chat_id'], card_id, reply_markup=keyboard)
                    #self.bot.edit_message_caption(body, params['chat_id'], card_id, reply_markup=keyboard)
                except:
                    self.send_card(func, nickname, call, params, backpath, card_id)

    def send_card(self, func, nickname, call, params, path, card_id=0):
        if params.get('photo') is None:
            if card_id == 0:
                if self.need_resend_menu(nickname):
                    self.resend_menu(call.message, path)
                result = func(**params).id
                self.udm.set_card_id(nickname, result)
                self.udm.save_message(params['chat_id'], result)
            else:
                self.delete(params['chat_id'], card_id)
                self.udm.delete_message(card_id)
                if self.need_resend_menu(nickname):
                    self.resend_menu(call.message, path)
                result = func(**params).id
                self.udm.set_card_id(nickname, result)
                self.udm.save_message(params['chat_id'], result)
            return
        with open(params['photo'], 'rb') as f:
            if card_id == 0:
                params['photo'] = f
                if self.need_resend_menu(nickname):
                    self.resend_menu(call.message, path)
                result = func(**params).id
                self.udm.set_card_id(nickname, result)
                self.udm.save_message(params['chat_id'], result)
            else:
                self.delete(params['chat_id'], card_id)
                self.udm.delete_message(card_id)
                params['photo'] = f
                if self.need_resend_menu(nickname):
                    self.resend_menu(call.message, path)
                result = func(**params).id
                self.udm.set_card_id(nickname, result)
                self.udm.save_message(params['chat_id'], result)

    def update_text_card(self, body, path, chat_id, message_id):
        try:
            self.bot.edit_message_caption(body, chat_id, message_id, reply_markup=self.get_comment_keyboard(path))
        except:
            self.bot.edit_message_text(body, chat_id, message_id, reply_markup=self.get_comment_keyboard(path))

    def delete(self, chat_id, message_id):
        try:
            self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

    def need_resend_menu(self, nickname):
        res = self.udm.get_user(nickname)
        return abs(res['menu_id'] - res['card_id']) == 1

    def send_menu(self, message, default_message='Используйте меню для навигации', path='start'):
        nickname = self.udm.get_nickname_by_message(message)
        markup = self.get_markup(self.sm.dynamic_search(path))
        if path != 'start':
            markup.row(self.get_back_button(self.get_backpath(path)))
        menu_id = self.bot.send_message(message.chat.id, text=default_message, reply_markup=markup).id
        if not self.udm.is_registered(nickname):
            self.udm.register_user(nickname, message.chat.id, menu_id)
            self.udm.save_message(message.chat.id, menu_id)
        else:
            self.udm.set_menu_id(nickname, menu_id)
            self.udm.set_card_id(nickname, 0)

    def resend_menu(self, message, path='start', default_message='Используйте меню для навигации'):
        nickname = self.udm.get_nickname_by_message(message)
        res = self.udm.get_user(nickname)
        self.delete(res['chat_id'], res['menu_id'])
        self.delete(res['chat_id'], res['card_id'])
        self.send_menu(message, default_message, path)
