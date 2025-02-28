import mysql.connector
from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    connections = mysql.connector.connect(
        host='host.docker.internal',
        user='root',
        password='MinMin123',
        database='user_base',
        port=3307
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
    app.run(debug=True)
