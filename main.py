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

bot.infinity_polling()
