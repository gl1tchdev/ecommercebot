import time
from threading import Thread
from telebot.util import extract_arguments, is_command
from managers.MessageManager import MessageManager
from managers.UserDataManager import UserDataManager
from decorators.Access import *
import config

mm = MessageManager()
bot = mm.get_bot()
udm = UserDataManager()

welcome = lambda text: config.welcome_message % text

def simple_reply(message, text):
    result = bot.send_message(message.chat.id, text).id
    udm.save_message(message.chat.id, result)
    return result


def reply_menu(message, markup, text=''):
    nickname = udm.get_nickname_by_message(message)
    udm.update_online(nickname)
    menu_id = udm.get_menu_id(nickname)
    bot.edit_message_reply_markup(message.chat.id, menu_id, reply_markup=markup)


def optional_reply(message, text, markup):
    result = bot.send_message(message.chat.id, text, reply_markup=markup).id
    udm.save_message(message.chat.id, result)


def safe_delete(chat_id, message_id, nickname):
    time.sleep(1)
    mm.delete(chat_id, message_id)
    udm.set_card_id(nickname, 0)


@bot.message_handler(commands=['menu'])
@registered
def resend(message):
    mm.resend_menu(message, default_message=welcome(message.from_user.first_name))


@bot.message_handler(commands=['start'])
@whitelist
def send_welcome(message):
    mm.send_menu(message, welcome(message.from_user.first_name))


@bot.message_handler(content_types=['text'], func=lambda
        message: message.reply_to_message and message.reply_to_message.text == 'Напишите текст для поиска:')
@registered
def search_func(message):
    squery = message.text
    result = mm.search(squery)
    if result is None:
        simple_reply(message, 'Ничего не найдено')
        return
    mm.resend_menu(message, default_message=welcome(message.from_user.first_name))
    reply_menu(message, result, 'Результаты поиска:')


@bot.message_handler(content_types=['text'], func=lambda
        message: message.reply_to_message and 'Напишите комментарий:' in message.reply_to_message.text)
@registered
def comment_func(message):
    text = message.text
    item_id = message.reply_to_message.text.split('\n')[0]
    if len(text) > 4095:
        simple_reply(message, 'Комментарий не может содержать больше 4096 символов')
        return
    mm.create_comment(item_id, message.from_user.username, text)
    p = mc.force_search_by_id(mm.sm.get_search_list(), item_id, True)
    path = mm.sm.get_path_by_query(p[0], p[1])
    item = mm.sm.dynamic_search(path)
    item.pop(0)
    item.pop(len(item) - 1)
    text = mm.make_body(item)
    nickname = udm.get_nickname_by_message(message)
    card_id = udm.get_card_id(nickname)
    mm.update_text_card(text, path, message.chat.id, card_id)


@bot.message_handler(content_types=['text'],
                     func=lambda message: not message.reply_to_message and not is_command(message.text))
@whitelist
def every(message):
    nickname = udm.get_nickname_by_message(message)
    if not udm.is_registered(nickname):
        simple_reply(message, 'Вы не зарегистрированы. Напишите /start')



@bot.callback_query_handler(
    func=lambda call: not call.data == 'start/global_search' and not call.data.endswith('comment') and not call.data == 'start/ask_question')
@registered_query
def callback_worker(call):
    path = call.data
    if path.startswith('cache:'):
        tpath = path.split(':')[1]
        path = mm.mc.get_cache(key=tpath)
    backpath = mm.get_backpath(path)
    search = mm.sm.dynamic_search(path)
    nickname = udm.get_nickname_by_message(call.message)
    card_id = udm.get_card_id(nickname)
    if (path[-1].isdigit() or path == 'start') and (card_id != 0):
        templ = path.split('/')
        word = templ[len(templ) - 2]
        if word in mm.sm.TREE.TREE['start'].keys() or path == 'start':
            t = Thread(target=safe_delete, args=(call.message.chat.id, card_id,udm.get_nickname_by_message(call.message),))
            t.start()

    if type(search) is dict:
        keyboard = mm.get_markup(search)
        if path != 'start':
            keyboard.row(mm.get_back_button(backpath))
        reply_menu(call.message, keyboard)

    if type(search) is list:
        mm.process_card(search, call, path)

    if search is None:
        bot.answer_callback_query(callback_query_id=call.id, text='Ничего не найдено')
        return
    try:
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        pass


@bot.callback_query_handler(func=lambda call: call.data == 'start/global_search')
@registered_query
def search(call):
    force = mm.get_force_reply()
    optional_reply(call.message, 'Напишите текст для поиска:', force)
    try:
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        pass


@bot.callback_query_handler(func=lambda call: call.data.endswith('comment'))
@registered_query
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
    if len(args) == 0:
        whitelist = udm.get_whitelist()
        if len(whitelist) == 0:
            return
        users = '\n'.join([a['nickname'] for a in whitelist])
        simple_reply(message, users)
        return
    args = args.split(' ')
    nickname = args[0]
    res = mm.mc.find('whitelist', {'nickname': nickname})
    if len(res) > 0:
        udm.remove_from_whitelist(nickname)
        simple_reply(message, 'Пользователь удалён из списка')
    else:
        udm.add_to_whitelist(nickname)
        simple_reply(message, 'Пользователь добавлен в список')


@bot.message_handler(commands=['setrole'])
@admin
def set_role(message):
    args = extract_arguments(message.text).split(' ')
    nickname = args[0]
    if len(args) == 1:
        udm.set_role(nickname, UserRole.STAFF.value)
        simple_reply(message, 'Роль пользователя установлена на STAFF')
        return
    role = args[1]
    if role not in [e.value for e in UserRole]:
        simple_reply(message, 'Такой роли нет. Существующие роли: admin, staff, customer')
        return
    udm.set_role(nickname, role)
    simple_reply(message, 'Обновлено')

@bot.message_handler(commands=['users'])
@admin
def users(message):
    body = 'Список пользователей:\n\n'
    user_list = udm.get_users()
    for user in user_list:
        body += 'Никнейм: %s\n' % user['nickname']
        body += 'Дата регистрации: %s\n' % user['registration_time']
        body += 'Последний онлайн: %s\n' % user['last_online']
        body += 'Роль: %s\n' % user['role']
        body += '\n'
    simple_reply(message, body)

@bot.callback_query_handler(func=lambda call: call.data == 'start/ask_question')
@registered_query
def question(call):
    force = mm.get_force_reply()
    optional_reply(call.message, 'Напишите свой вопрос:', force)
    try:
        bot.answer_callback_query(callback_query_id=call.id)
    except:
        pass

@bot.message_handler(content_types=['text'], func=lambda
        message: message.reply_to_message and 'Напишите свой вопрос:' in message.reply_to_message.text)
def process_question(message):
    question = message.text
    user_nickname = udm.get_nickname_by_message(message)
    chat_id = udm.get_user(config.owner)['chat_id']
    body = 'Вопрос от @%s:\n%s' % (user_nickname, question)
    bot.send_message(chat_id, body)
    simple_reply(message, 'Ваш вопрос получен. Администратор свяжется с Вами в течение суток')

bot.infinity_polling()
