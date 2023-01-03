import telebot
from managers.MessageManager import MessageManager
import config

bot = telebot.TeleBot(config.token)
mm = MessageManager()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not mm.is_in_whitelist(message.from_user.username):
        return
    bot.reply_to(message, "Привет")

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if not mm.is_in_whitelist(call.message.from_user.username):
        return



bot.infinity_polling()
