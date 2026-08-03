import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import schedule
import time
import threading

bot=telebot.TeleBot('8953354779:AAEVWRhsADFt5NtNKJl0YUWAQ4275u0pva8')
user_action={}

@bot.message_handler(commands=['start'])
def send_welcome(message):


    conn=sqlite3.connect('data.sql')
    cur=conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, remind_time TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, date TEXT)')

    conn.commit()

    cur.execute("SELECT * FROM habits WHERE user_id=?",(message.from_user.id,))
    habits=cur.fetchall()

    cur.close()
    conn.close()


    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton('Создать новую привычку',callback_data='add'))
    markup.add(types.InlineKeyboardButton('Удалить привычку', callback_data='delete'))
    #markup.add(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark'))
    markup.add(types.InlineKeyboardButton('Мои привычки',callback_data='list'))
    markup.add(types.InlineKeyboardButton('Статистика', callback_data='stats'))

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

def streak(habit_id):

    conn = sqlite3.connect('data.sql')
    cur = conn.cursor()

    cur.execute("SELECT date FROM progress WHERE habit_id=?",(habit_id,))

    dates=cur.fetchall()

    conn.close()

    if not dates:
        return 0
    count=0

    today=datetime.now().date()

    for i,date in enumerate(dates):
        day=datetime.strptime(date[0],'%Y-%m-%d').date()

        expected_day=today - timedelta(days=i)

        if day==expected_day:
            count+=1
        else:break

    return count
@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if call.data=='add':
        user_action[call.message.chat.id]="waiting_name"
        bot.send_message(call.message.chat.id,"Напиши название привычки:")
    elif call.data=='delete':

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute("SELECT id, name FROM habits WHERE user_id=?", (call.from_user.id,))

        habits = cur.fetchall()

        conn.close()

        if not habits:
            make = types.InlineKeyboardMarkup()
            make.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))

            bot.send_message(call.message.chat.id, 'У тебя нет привычек для удаления.', reply_markup=make)
        else:
            for habit in habits:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Удалить", callback_data=f"delete_{habit[0]}"))

                bot.send_message(call.message.chat.id, f"{habit[1]}", reply_markup=markup)
    #elif call.data=='mark':
    #   bot.send_message(call.message.chat.id,"Отмечание")
    elif call.data=='list':

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute("SELECT id, name FROM habits WHERE user_id=?", (call.from_user.id,))

        habits=cur.fetchall()

        conn.close()

        if not habits:
            make = types.InlineKeyboardMarkup()
            make.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))

            bot.send_message(call.message.chat.id, 'У тебя пока нет привычек.\nДобавим новую?', reply_markup=make)
        else:
            for habit in habits:

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Выполнено", callback_data=f"done_{habit[0]}"))

                bot.send_message(call.message.chat.id,f"{habit[1]}",reply_markup=markup)
    elif call.data.startswith('delete_'):
        habit_id = call.data.split('_')[1]
        #habit_id = int(habit_id)
        #print("call.data =", call.data)

        #parts = call.data.split("_")
        #print(parts)
        #print("Удаляем habit_id =", habit_id)


        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        cur.execute("DELETE FROM progress WHERE habit_id=?",(habit_id,))
        cur.execute("DELETE FROM habits WHERE id=?", (habit_id,))

        conn.commit()

        conn.close()

        bot.answer_callback_query(call.id, "Привычка удалена")

        bot.delete_message(call.message.chat.id,call.message.message_id)

    elif call.data.startswith('done_'):
        habit_id = call.data.split('_')[1]

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        cur.execute("INSERT INTO progress(habit_id, date) VALUES(?,?)",(habit_id, today))

        conn.commit()

        conn.close()

        bot.answer_callback_query(call.id, "Молодец! Привычка выполнена")

        bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,reply_markup=None)
    elif call.data=='stats':

        conn = sqlite3.connect('data.sql')
        cur = conn.cursor()

        cur.execute("SELECT habits.name, COUNT(progress.id) FROM habits LEFT JOIN progress ON habits.id = progress.habit_id WHERE habits.user_id=? GROUP BY habits.id, habits.name",(call.from_user.id,))

        result=cur.fetchall()

        #print(result)

        conn.close()

        if not result:
            stat = types.InlineKeyboardMarkup()
            stat.add(types.InlineKeyboardButton('Мои привычки', callback_data='list'))
            bot.send_message(call.message.chat.id,"У тебя пока нет выполненых привычек.\nДавай сделаем их.",reply_markup=stat)
        else:
            text="Твоя статистика:\n\n"

            markup = types.InlineKeyboardMarkup()

            markup.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))
            markup.add(types.InlineKeyboardButton('Удалить привычку', callback_data='delete'))
            # markup.add(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark'))
            markup.add(types.InlineKeyboardButton('Мои привычки', callback_data='list'))
            markup.add(types.InlineKeyboardButton('Статистика', callback_data='stats'))

            for habit in result:
                #text+=f"{habit[0]} - {habit[1]} раз\n"
                my_streak=streak(habit[0])
                text+=(f"{habit[0]}\n"f"Выполнено: {habit[1]} раз\n"f"🔥 Серия: {my_streak} дней\n\n")
            text+="Ты молодец!!!"
            bot.send_message(call.message.chat.id,text,reply_markup=markup)


@bot.message_handler(func=lambda message: user_action.get(message.chat.id)=="waiting_name")
def save_name(message):
    user_action[message.chat.id] = {"name": message.text}

    user_action[message.chat.id]["step"] = "waiting_time"

    bot.send_message(message.chat.id,"Во сколько напоминать?\nНапример: 09:00")


#@bot.message_handler(func=lambda message: user_action.get(message.chat.id)=="waiting_time")
@bot.message_handler(func=lambda message:isinstance(user_action.get(message.chat.id), dict) and user_action[message.chat.id].get("step")=="waiting_time")
def save_time(message):

    habit = user_action[message.chat.id]

    conn=sqlite3.connect('data.sql')
    cur=conn.cursor()

    cur.execute("INSERT INTO habits(user_id,name,remind_time) VALUES(?,?,?)",(message.from_user.id, habit["name"],message.text))

    conn.commit()

    cur.close()
    conn.close()

    user_action.pop(message.chat.id)

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton('Создать новую привычку', callback_data='add'))
    markup.add(types.InlineKeyboardButton('Удалить привычку', callback_data='delete'))
    # markup.add(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark'))
    markup.add(types.InlineKeyboardButton('Мои привычки', callback_data='list'))
    markup.add(types.InlineKeyboardButton('Статистика', callback_data='stats'))

    bot.send_message(message.chat.id,f"✅ {habit['name']} добавлена\n"f"⏰ Напоминание: {message.text}",reply_markup=markup)

def reminder():
    while True:
        now = datetime.now().strftime("%H:%M")

        conn=sqlite3.connect('data.sql')
        cur=conn.cursor()

        cur.execute("SELECT user_id,name FROM habits WHERE remind_time=?",(now,))

        habits=cur.fetchall()

        conn.close()

        for habit in habits:
            bot.send_message(habit[0],f"⏰ Пора выполнить привычку: {habit[1]}")

        time.sleep(60)



threading.Thread(target=reminder).start()
bot.polling(none_stop=True)