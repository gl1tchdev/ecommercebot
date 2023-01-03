from telebot import types
from classes.Singleton import Singleton
from managers.DbSearchManager import SearchManager
import config


class MessageManager(Singleton):

    sm = SearchManager()

    def is_in_whitelist(self, nickname):
        return True if nickname in config.whitelist else False

    def get_markup(self, dict):
        keyboard = types.InlineKeyboardMarkup()
        for key in dict:
            keyboard.row(types.InlineKeyboardButton(text=key, callback_data=dict[key]))
        return keyboard

    def get_start(self):
        return self.sm.dynamic_search('start/devices')