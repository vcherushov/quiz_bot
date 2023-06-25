import telebot
from telebot import types
import threading
import time

import sqlite3

TOKEN = '5849486081:AAHE9dzcXmE_7EgZOhTFAxun0CFdGgkHHh8'
bot = telebot.TeleBot(TOKEN)

questions = [
    {
        "question": "2 + 2",
        "answers": ["2", "10", "4", "3"],
        "correct_answer": "4"
    },
    {
        "question": "3 + 3",
        "answers": ["6", "8", "1", "7"],
        "correct_answer": "6"
    },
    {
        "question": "6 + 6",
        "answers": ["12", "13", "14", "15"],
        "correct_answer": "12"
    },
    {
        "question": "4 + 4",
        "answers": ["8", "10", "1", "22"],
        "correct_answer": "8"
    },
    {
        "question": "5 + 5",
        "answers": ["11", "10", "15", "5"],
        "correct_answer": "10"
    },
    {
        "question": "7 + 7",
        "answers": ["21", "28", "14", "7"],
        "correct_answer": "14"
    },
    {
        "question": "1 + 1",
        "answers": ["2", "3", "1", "11"],
        "correct_answer": "2"
    }
]

user_answers = {}

def timeout(user_id, question_index):

    # Время ожидания для каждого из вопросов
    wait_time =[30, 15, 15, 15, 15, 15, 15]
    time.sleep(wait_time[question_index])

    if len(user_answers[user_id]) == question_index:
        user_answers[user_id].append(False)
        bot.send_message(chat_id=user_id, text="Время вышло.")

def reset_quiz():
    user_answers = {}
    correct_count = 0

@bot.message_handler(commands=['start'])
def handle_start(message):
    # Сбрасываем ответы пользователя при каждом запуске опроса
    user_id = message.chat.id
    user_answers[user_id] = []
    user_answers[message.chat.id] = []
    
    bot.send_message(chat_id=message.chat.id, text="Привет! Я бот-квиз. Ответь на 7 вопросов.")
    
    # Задаем первый вопрос и кнопки с вариантами ответов
    current_question_index = 0
    question = questions[current_question_index]
    buttons = types.ReplyKeyboardMarkup(row_width=2)
    for answer in question['answers']:
        button = types.KeyboardButton(answer)
        buttons.add(button)

    bot.send_message(chat_id=message.chat.id, text=f"{current_question_index+1}. {question['question']}", reply_markup=buttons)
        
    # запускаем таймер для этого вопроса
    t = threading.Thread(target=timeout, args=(message.chat.id, current_question_index))
    t.start()

    # Перенаправляем пользователя на функцию обработки ответов
    bot.register_next_step_handler(message, handle_answer)


@bot.message_handler(commands=['restart'])
def restart_quiz(message):
    user_id = message.chat.id
    user_answers[user_id] = []
    user_answers[message.chat.id] = []
    handle_start(message)


@bot.message_handler(content_types=['text'])
def handle_answer(message):
    user_id = message.chat.id
    
    # Проверяем, является ли сообщение командой или не написанно ли оно просто так
    if (message.text.startswith('/')) or (len(user_answers[user_id]) >= len(questions)):
        return
    
    if user_id not in user_answers:
        user_answers[user_id] = []
    current_question_index = len(user_answers[user_id])
    correct_answer = questions[current_question_index]['correct_answer']
    
    if message.text == correct_answer:
        bot.send_message(chat_id=user_id, text="Верно!")
        user_answers[user_id].append(True)
    else:
        bot.send_message(chat_id=user_id, text="Неверно.")
        user_answers[user_id].append(False)
    
    # проверяем, есть ли еще вопросы
    if current_question_index == len(questions) - 1:
        total_correct_answers = sum(user_answers[user_id])
        
        if total_correct_answers == len(questions):
            bot.send_message(chat_id=user_id, text="Поздравляю! Вы правильно ответили на все вопросы.")
        else:
            bot.send_message(chat_id=user_id, text=f"Вы ответили правильно на {total_correct_answers} из {len(questions)} вопросов. Попробуйте еще раз.")
        
        remove_keyboard = types.ReplyKeyboardRemove()
        bot.send_message(chat_id=user_id, text="Конец опроса.", reply_markup=remove_keyboard)

        user_name = message.from_user.username
        add_winners_to_database(user_name)

    else:
        # задаем следующий вопрос и кнопки с вариантами ответов
        next_question = questions[current_question_index + 1]
        buttons = types.ReplyKeyboardMarkup(row_width=2)
        for answer in next_question['answers']:
            button = types.KeyboardButton(answer)
            buttons.add(button)
        
        bot.send_message(chat_id=message.chat.id, text=f"{current_question_index+2}. {next_question['question']}", reply_markup=buttons)
        
        # запускаем таймер для этого вопроса
        t = threading.Thread(target=timeout, args=(message.chat.id, current_question_index + 1))
        t.start()

        # Перенаправляем пользователя на эту же функцию обработки ответов
        bot.register_next_step_handler(message, handle_answer)

def add_winners_to_database(user_name):
    connection = sqlite3.connect('quiz.db')
    cursor = connection.cursor()

    # проверяем, есть ли пользователь уже в таблице
    cursor.execute("SELECT * FROM winners WHERE username=?", (user_name,))
    user_exists = cursor.fetchone()

    if user_exists:
        print("User is already in the table.")
    else:
        cursor.execute("INSERT INTO winners (username) VALUES (?)", (user_name,))
        connection.commit()
        print("User has been added to the table.")

    connection.close()




bot.polling()
