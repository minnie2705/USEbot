import mysql.connector
from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    connections = mysql.connector.connect(
        host='localhost',
        user='root',
        password='MinMin123',
        database='user_base'
    )
    cur = connections.cursor()

    que = 'SELECT * FROM user_base'
    cur.execute(que)
    result = cur.fetchall()

    data = [' ||| '.join([str(line[0])] + list(map(str, line[1:]))) for line in result]

    cur.close()
    connections.close()

    return render_template('index.html', items=data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
