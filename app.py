# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pyotp

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    accounts = conn.execute('SELECT * FROM accounts').fetchall()
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

        conn = get_db_connection()
        conn.execute('INSERT INTO accounts (avatar, nickname, login, password, fa_code, uid) VALUES (?, ?, ?, ?, ?, ?)',
                     (avatar, nickname, login, password, fa_secret, uid))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    account = conn.execute('SELECT * FROM accounts WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        avatar = request.form['avatar']
        nickname = request.form['nickname']
        login = request.form['login']
        password = request.form['password']
        fa_secret = request.form['fa_code']
        uid = request.form['uid']

        conn.execute('UPDATE accounts SET avatar = ?, nickname = ?, login = ?, password = ?, fa_code = ?, uid = ? WHERE id = ?',
                     (avatar, nickname, login, password, fa_secret, uid, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('edit.html', account=account)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM accounts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
