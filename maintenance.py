from managers.MessageManager import MessageManager

mm = MessageManager()
bot = mm.get_bot()
text = 'В данный момент ведутся технические работы. Бот не может обрабатывать нажатия кнопок и отвечать на сообщения. Пожалуйста, ожидайте.'

@bot.message_handler(func=lambda message: True)
def maintenance(message):
    bot.send_message(chat_id=message.chat.id, text=text)

@bot.callback_query_handler(func=lambda call: True)
def maintenance_call(call):
    bot.send_message(chat_id=call.message.chat.id, text=text)
    bot.answer_callback_query(call.id, text=text)

bot.infinity_polling()
