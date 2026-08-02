import telebot

bot=telebot.TeleBot('8953354779:AAEVWRhsADFt5NtNKJl0YUWAQ4275u0pva8')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Привет!')


