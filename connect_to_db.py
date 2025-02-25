import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='MinMin123',
    database='user_base'
)

# Проверим подключение
if connection.is_connected():
    print("Успешное подключение к базе данных!")
else:
    print("Ошибка подключения.")
