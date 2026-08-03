from fileinput import close

import telebot
from telebot import types
import sqlite3

bot=telebot.TeleBot('8953354779:AAEVWRhsADFt5NtNKJl0YUWAQ4275u0pva8')

@bot.message_handler(commands=['start'])
def send_welcome(message):


    conn=sqlite3.connect('data.sql')
    cur=conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS habits (id int auto_increment primary key, user_id INTEGER, name TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS progress(id int auto_increment primary key, habit_id INTEGER, date TEXT)')
    #cur.execute('CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT)')
    #cur.execute('CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, date TEXT)')

    conn.commit()

    cur.execute("SELECT * FROM habits WHERE user_id=?",(message.from_user.id,))
    habits=cur.fetchall()

    cur.close()
    conn.close()


    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton('Создать новую привычку',callback_data='add'))
    markup.add(types.InlineKeyboardButton('Удалить привычку', callback_data='delete'))
    markup.add(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark'))

    make = types.InlineKeyboardMarkup()
    make.add(types.InlineKeyboardButton('Создать новую привычку',callback_data='add'))

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!')
    if not habits:
        bot.send_message(message.chat.id, 'У тебя пока нет привычек.\nДобавим новую?',reply_markup=make)
        #bot.send_message(message.chat.id,'Добавим новую?',reply_markup=make)
        #markup.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))
    else:
        bot.send_message(message.chat.id,'Ваше меню:', reply_markup=markup)
#def add_habit(message):
 @bot.callback_query_handler(func=lambda call: True)
 def button(call):
    if call.data=='add':
        bot.send_message(call.messege.chat.id,"Напиши название привычки:")
    elif call.data=='delete':
        bot.send_message(call.messege.chat.id,"Удаление")
    elif call.data=='mark':
        bot.send_message(call.messege.chat.id,"Отмечание")
bot.polling(none_stop=True)