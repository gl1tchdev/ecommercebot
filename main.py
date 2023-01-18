from telebot.apihelper import ApiTelegramException
from telebot.util import extract_arguments, is_command
from managers.MessageManager import MessageManager
from managers.UserDataManager import UserDataManager
from decorators.Access import *

mm = MessageManager()
bot = mm.get_bot()
udm = UserDataManager()
default_message = 'Используйте меню для навигации'



def simple_reply(message, text):
    nickname = udm.get_nickname_by_message(message)
    if not udm.is_registered(nickname):
        udm.register_user(nickname)
    if not udm.has_last_message(nickname):
        udm.add_data(nickname, message.id)
    result = bot.send_message(message.chat.id, text)
    udm.set_last_message(nickname, result.id)


def default_reply(message, markup):
    global default_message
    nickname = udm.get_nickname_by_message(message)
    if not udm.has_last_message(nickname):
        udm.add_data(nickname, message.id)
    last_message = udm.get_last_message(nickname)
    try:
        bot.edit_message_reply_markup(message.chat.id, last_message, reply_markup=markup)
    except:
        result = bot.send_message(message.chat.id, default_message, reply_markup=markup)
        udm.set_last_message(nickname, result.id)

def optional_reply(message, text, markup):
    global default_message
    nickname = udm.get_nickname_by_message(message)
    if not udm.is_registered(nickname):
        udm.register_user(nickname)
    if not udm.has_last_message(nickname):
        udm.add_data(nickname, message.id)
    last_message = udm.get_last_message(nickname)
    try:
        bot.edit_message_reply_markup(message.chat.id, last_message, reply_markup=markup)
    except ApiTelegramException:
        result = bot.send_message(message.chat.id, text, reply_markup=markup)
        udm.set_last_message(nickname, result.id)
        return
    try:
        bot.edit_message_text(text, message.chat.id, message.id)
    except:
        result = bot.send_message(message.chat.id, text, reply_markup=markup)
        udm.set_last_message(nickname, result.id)





@bot.message_handler(commands=['start', 'menu'])
@whitelist
def send_welcome(message):

    default_reply(message, mm.get_start())



@bot.message_handler(content_types=['text'], func=lambda message: message.reply_to_message and message.reply_to_message.text == 'Напишите текст для поиска:')
@whitelist
def search_func(message):
    squery = message.text
    result = mm.search(squery)
    if result is None:
        optional_reply(message, 'Ничего не найдено', mm.get_back_button('start', True))
        return
    optional_reply(message, 'Результаты поиска:', result)

@bot.message_handler(content_types=['text'], func=lambda message: message.reply_to_message and 'Напишите комментарий:' in message.reply_to_message.text)
@whitelist
def comment_func(message):
    text = message.text
    item_id = message.reply_to_message.text.split('\n')[0]
    mm.create_comment(item_id, message.from_user.username, text)
    simple_reply(message, 'Вы успешно оставили комментарий')
    default_reply(message, mm.get_start())


@bot.callback_query_handler(func=lambda call: call.data.startswith('search'))
@whitelist_query
def search_callback(call):
    query = call.data.split('"')
    result = mm.search(query[1])
    if result is None:
        optional_reply(call.message, 'Ничего не найдено', mm.get_back_button('start', True))
        return
    optional_reply(call.message, 'Результаты поиска:', result)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(content_types=['text'], func=lambda message: not message.reply_to_message and not is_command(message.text))
@whitelist
def every(message):
    default_reply(message, mm.get_start())


@bot.callback_query_handler(func=lambda call: not call.data == 'start/global_search' and not call.data.endswith('comment'))
@whitelist_query
def callback_worker(call):
    path = call.data
    if path.startswith('cache:'):
        tpath = path.split(':')[1]
        path = mm.mc.get_cache(key=tpath)
    backpath = mm.get_backpath(path)
    search = mm.sm.dynamic_search(path)
    if type(search) is dict:
        keyboard = mm.get_markup(search)
        if path != 'start':
            keyboard.row(mm.get_back_button(backpath))
        default_reply(call.message, keyboard)

    if type(search) is list:
        mm.process_card(search, call, path)

    if search is None:
        bot.answer_callback_query(callback_query_id=call.id, text='Ничего не найдено')
        default_reply(call.message, mm.get_start())
        return
    try:
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'start/global_search')
@whitelist_query
def search(call):
    force = mm.get_force_reply()
    optional_reply(call.message, 'Напишите текст для поиска:', force)
    try:
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data.endswith('comment'))
@whitelist_query
def comment(call):
    path = mm.get_backpath(call.data)
    info = mm.get_info_comment(path)
    text = info + '\n' + 'Напишите комментарий:'
    optional_reply(call.message, text, mm.get_force_reply())
    bot.answer_callback_query(callback_query_id=call.id)

@bot.message_handler(commands=['whitelist'])
@admin
def whitelist(message):
    args = extract_arguments(message.text)
    nickname = args[0]
    udm.add_to_whitelist(nickname)
    simple_reply(message, 'Добавлено')

@bot.message_handler(commands=['setrole'])
@admin
def set_role(message):
    args = extract_arguments(message.text)
    nickname = args[0]
    role = args[1]
    if role not in [e.value for e in UserRole]:
        return
    udm.set_role(nickname, role)
    simple_reply(message, 'Обновлено')


bot.infinity_polling()
