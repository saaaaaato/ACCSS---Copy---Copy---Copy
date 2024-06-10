from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2
import pyotp
import bcrypt
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')
csrf = CSRFProtect(app)

def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM accounts')
    accounts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', accounts=accounts)

@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        avatar = request.form['avatar']
        nickname = request.form['nickname']
        login = request.form['login']
        password = request.form['password']
        fa_secret = pyotp.random_base32()
        uid = request.form['uid']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO accounts (avatar, nickname, login, password, fa_code, uid) VALUES (%s, %s, %s, %s, %s, %s)',
                    (avatar, nickname, login, hashed_password, fa_secret, uid))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM accounts WHERE id = %s', (str(id),))
    account = cur.fetchone()

    if request.method == 'POST':
        avatar = request.form['avatar']
        nickname = request.form['nickname']
        login = request.form['login']
        password = request.form['password']
        fa_secret = request.form['fa_code']
        uid = request.form['uid']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur.execute('UPDATE accounts SET avatar = %s, nickname = %s, login = %s, password = %s, fa_code = %s, uid = %s WHERE id = %s',
                    (avatar, nickname, login, hashed_password, fa_secret, uid, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', account=account)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM accounts WHERE id = %s', (str(id),))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
