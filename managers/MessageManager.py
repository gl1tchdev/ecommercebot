from telebot import types
from managers.SheetDataValidationManager import SheetManager
import config


class MessageManager:
    ierarchy = ['start', 'manufacturers', 'models']

    vm = SheetManager()

    def is_in_whitelist(self, nickname):
        return True if nickname in config.whitelist else False

    def get_markup(self, dict, location='start'):
        keyboard = types.InlineKeyboardMarkup()
        for key in dict:
            keyboard.row(types.InlineKeyboardButton(text=dict[key], callback_data='button %s' % key))
        if location != 'start':
            keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data='back %s' % location))
        return keyboard

    def get_start_markup(self, manufacturers):
        return