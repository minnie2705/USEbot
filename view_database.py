import mysql.connector
from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    # Устанавливаем подключение к MySQL
    connections = mysql.connector.connect(
        host='localhost',  # адрес сервера MySQL
        user='root',  # ваше имя пользователя MySQL
        password='MinMin123',  # ваш пароль MySQL
        database='user_base'  # имя базы данных
    )
    cur = connections.cursor()

    que = 'SELECT * FROM user_base'
    cur.execute(que)
    result = cur.fetchall()

    # Преобразуем данные в строковый вид для отображения
    data = [' ||| '.join([str(line[0])] + list(map(str, line[1:]))) for line in result]

    # Закрываем соединение
    cur.close()
    connections.close()

    return render_template('index.html', items=data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
