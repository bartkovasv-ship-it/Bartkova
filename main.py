from fileinput import close

import telebot
from telebot import types
import sqlite3
from datatime import datetime

bot=telebot.TeleBot('8953354779:AAEVWRhsADFt5NtNKJl0YUWAQ4275u0pva8')
user_action={}
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
    markup.add(types.InlineKeyboardButton('Мои привычки',callback_data='list'))

    make = types.InlineKeyboardMarkup()
    make.add(types.InlineKeyboardButton('Создать новую привычку',callback_data='add'))

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!')
    if not habits:
        bot.send_message(message.chat.id, 'У тебя пока нет привычек.\nДобавим новую?',reply_markup=make)
        #bot.send_message(message.chat.id,'Добавим новую?',reply_markup=make)
        #markup.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))
    else:
        bot.send_message(message.chat.id,'Ваше меню:', reply_markup=markup)
#def add_habit(message):ъ


@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if call.data=='add':
        user_action[call.message.chat.id]="add_habit"
        bot.send_message(call.message.chat.id,"Напиши название привычки:")
    elif call.data=='delete':
        bot.send_message(call.message.chat.id,"Удаление")
    elif call.data=='mark':
        bot.send_message(call.message.chat.id,"Отмечание")
    elif call.data=='list':

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute("SELECT id, name FROM habits WHERE user_id=?", (call.from_user.id,))

        habits=cur.fetchall()

        conn.close()

        if not habits:
            bot.send_message(message.chat.id, 'У тебя пока нет привычек.\nДобавим новую?', reply_markup=make)
        else:
            for habit in habits:

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Выполнено", callback_data=f"done_{habit[0]}"))

                bot.send_message(call.message.chat.id,f"{habit[1]}",reply_markup=markup)
@bot.message_handler(func=lambda message: user_action.get(message.chat.id)=="add_habit")
def save_habits(message):
    conn=sqlite3.connect('data.sql')
    cur=conn.cursor()

    cur.execute("INSERT INTO habits(user_id,name) VALUES(?,?)",(message.from_user.id,message.text))

    conn.commit()

    cur.close()
    conn.close()

    user_action.pop(message.chat.id)

    bot.send_message(message.chat.id,f"Привычка '{message.text}' добавлена!")


bot.polling(none_stop=True)