import mysql.connector
from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    connections = mysql.connector.connect(
        host='mysql_container',
        user='root',
        password='MinMin123',
        database='ege'
    )
    cur = connections.cursor()

    que = 'SELECT * FROM ege'
    cur.execute(que)
    result = cur.fetchall()

    data = [' ||| '.join([str(line[0])] + list(map(str, line[1:]))) for line in result]

    cur.close()
    connections.close()

    return render_template('index.html', items=data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
