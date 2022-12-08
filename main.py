import telebot
bot = telebot.TeleBot('5915328814:AAGhMOQCV016JXQNdvcADQ91L_Yqa6zSHkE')



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет")


bot.infinity_polling()
