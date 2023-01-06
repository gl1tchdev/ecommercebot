import telebot
from managers.MessageManager import MessageManager
import config

bot = telebot.TeleBot(config.token, parse_mode='MARKDOWN')
mm = MessageManager()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not mm.is_in_whitelist(message.from_user.username):
        return
    bot.reply_to(message, "Используй меню для навигации", reply_markup=mm.get_start())

@bot.message_handler(func=lambda message: True)
def every(message):
    if not mm.is_in_whitelist(message.from_user.username):
        return
    bot.reply_to(message, "Используй меню для навигации", reply_markup=mm.get_start())


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if not mm.is_in_whitelist(call.message.chat.username):
        return
    path = call.data
    backpathm = path.split('/')
    backpathm.pop(len(backpathm) - 1)
    backpath = '/'.join(backpathm)
    search = mm.sm.dynamic_search(path)

    if type(search) is dict:
        keyboard = mm.get_markup(search)
        if path != 'start':
            keyboard.row(mm.get_back_button(backpath))
        bot.send_message(call.message.chat.id, 'Используй меню для навигации', reply_markup=keyboard)
    if type(search) is list:
        result = mm.process_card(search, call.message, backpath, bot)
        result[0](**result[1])

    if search is None:
        bot.send_message(call.message.chat.id, 'Ничего не найдено', reply_markup=mm.get_back_button(backpath, True))
    bot.answer_callback_query(callback_query_id=call.id)

bot.infinity_polling()
