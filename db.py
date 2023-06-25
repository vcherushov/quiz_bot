import sqlite3

# Создаем таблицу для хранения пользователей, ответивших на все вопросы верно
#conn = sqlite3.connect('quiz.db')
#cursor = conn.cursor()
#cursor.execute('''CREATE TABLE winners (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
#conn.commit()
#conn.close()


# Вывод всех пользователей из таблицы
connection = sqlite3.connect('quiz.db')
cursor = connection.cursor()

cursor.execute("SELECT * FROM winners")

results = cursor.fetchall()

connection.close()

for row in results:
    print(row)