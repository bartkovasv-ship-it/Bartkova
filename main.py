import telebot
from telebot import types

bot=telebot.TeleBot('8953354779:AAEVWRhsADFt5NtNKJl0YUWAQ4275u0pva8')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Создать новую привычку',callback_data='make'))
    markup.add(types.InlineKeyboardButton('Удалить привычку', callback_data='delete'))
    markup.add(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark'))
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!')


bot.polling(none_stop=True)