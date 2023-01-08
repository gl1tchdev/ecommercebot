import telebot
from managers.MessageManager import MessageManager
from managers.FunctionsManager import FunctionsManager
import config

bot = telebot.TeleBot(config.token, parse_mode='HTML')
mm = MessageManager()
fm = FunctionsManager()
default_reply = lambda message, markup: bot.send_message(message.chat.id, 'Используй меню для навигации', reply_markup=markup)
simple_reply = lambda message, text: bot.send_message(message.chat.id, text)
optional_reply = lambda message, text, markup: bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not mm.is_in_whitelist(message.from_user.username):
        return
    default_reply(message, mm.get_start())

@bot.message_handler(content_types=['text'], func=lambda message: message.reply_to_message and message.reply_to_message.text == 'Напиши текст для поиска:')
def search_func(message):
    if not mm.is_in_whitelist(message.from_user.username):
        return
    squery = message.text
    result = mm.search(squery)
    if result is None:
        optional_reply(message, 'Ничего не найдено', mm.get_back_button('start', True))
        return
    optional_reply(message, 'Результаты поиска:', result)


@bot.callback_query_handler(func=lambda call: call.data.startswith('search'))
def search_callback(call):
    if not mm.is_in_whitelist(call.message.chat.username):
        return
    query = call.data.split('"')
    result = mm.search(query[1])
    if result is None:
        optional_reply(call.message, 'Ничего не найдено', mm.get_back_button('start', True))
        return
    optional_reply(call.message, 'Результаты поиска:', result)
    bot.answer_callback_query(callback_query_id=call.id)

@bot.message_handler(content_types=['text'], func=lambda message: not message.reply_to_message)
def every(message):
    if not mm.is_in_whitelist(message.from_user.username):
        return
    default_reply(message, mm.get_start())


@bot.callback_query_handler(func=lambda call: not call.data == 'start/global_search')
def callback_worker(call):
    if not mm.is_in_whitelist(call.message.chat.username):
        return
    path = call.data
    s_search = ''
    if '|' in path:
        temp = path.split('|')
        path = temp[0]
        s_search = temp[1]
    backpathm = path.split('/')
    backpathm.pop(len(backpathm) - 1)
    backpath = '/'.join(backpathm)
    search = mm.sm.dynamic_search(path)
    if type(search) is dict:
        keyboard = mm.get_markup(search)
        if path != 'start':
            keyboard.row(mm.get_back_button(backpath))
        default_reply(call.message, keyboard)
    if type(search) is list:
        if not s_search:
            result = mm.process_card(search, call, backpath, bot)
        else:
            result = mm.process_card(search, call, s_search, bot)
        result[0](**result[1])

    if search is None:
        bot.answer_callback_query(callback_query_id=call.id, text='Ничего не найдено')
        default_reply(call.message, mm.get_start())
        return
    bot.answer_callback_query(callback_query_id=call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'start/global_search')
def search(call):
    force = mm.get_force_reply()
    optional_reply(call.message, 'Напиши текст для поиска:', force)
    bot.answer_callback_query(callback_query_id=call.id)

bot.infinity_polling()
