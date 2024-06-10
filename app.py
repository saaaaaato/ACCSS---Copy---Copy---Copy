from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pyotp
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db/database.db')
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.String(200))
    nickname = db.Column(db.String(200))
    login = db.Column(db.String(200))
    password = db.Column(db.String(200))
    fa_code = db.Column(db.String(32))
    uid = db.Column(db.String(200))

@app.route('/')
def index():
    accounts = Account.query.all()
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

        new_account = Account(avatar=avatar, nickname=nickname, login=login, password=password, fa_code=fa_secret, uid=uid)
        db.session.add(new_account)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    account = Account.query.get(id)

    if request.method == 'POST':
        account.avatar = request.form['avatar']
        account.nickname = request.form['nickname']
        account.login = request.form['login']
        account.password = request.form['password']
        account.fa_code = request.form['fa_code']
        account.uid = request.form['uid']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', account=account)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    account = Account.query.get(id)
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/2fa/<int:id>')
def two_factor_auth(id):
    account = Account.query.get(id)
    if account:
        totp = pyotp.TOTP(account.fa_code)
        return totp.now()
    return "Account not found", 404

if __name__ == "__main__":
    app.run(debug=True)
