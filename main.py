from fileinput import close

import telebot
from telebot import types
import sqlite3

bot=telebot.TeleBot('8953354779:AAEVWRhsADFt5NtNKJl0YUWAQ4275u0pva8')

@bot.message_handler(commands=['start'])
def send_welcome(message):


    conn=sqlite3.connect('data.sql')
    cur=conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS habits (id int auto_increment primary key, user_id integer, name varchar(255))')
    cur.execute('CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, date TEXT)')
    conn.commit()
    cur.close()
    conn.close()


    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Создать новую привычку',callback_data='add'))
    markup.add(types.InlineKeyboardButton('Удалить привычку', callback_data='delete'))
    markup.add(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark'))

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!')
    if not habits:
        bot.send_message(message.chat.id, 'У вас пока нет привычек.')
        bot.send_message(message.chat.id,'Добавим новую?')
        markup.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))

#def add_habit(message):
    
bot.polling(none_stop=True)