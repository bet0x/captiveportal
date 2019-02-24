from flask import Flask, render_template, request, flash, redirect
import sqlite3
import os
from ipa_auth import ipa_login, isAdmin, get_admin_group


app = Flask(__name__)



def ban_user(user):
    # TODO: remove form IPTABLES, and release IP in DHCP
    try:
        db_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'user-ip.db')
        db = sqlite3.connect(db_file)
        cursor = db.cursor()

        user_to_remove = user

        cursor.execute("SELECT ip FROM clients WHERE username = ?", [user_to_remove])

        for ip in cursor.fetchall():
            ip = str(ip)[2:-3]
            print(ip)
            cursor.execute('DELETE FROM clients WHERE ip = ?', [str(ip)])

        cursor.execute('INSERT INTO banned_users VALUES(?)', [user_to_remove])

        db.commit()
        return True
    except Exception as e:
        print(e)
        return False



@app.route('/admin', methods=["GET"])
def admin_page():

    db_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'user-ip.db')
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    cursor.execute("SELECT * FROM clients")
    data = cursor.fetchall()

    cursor.execute("SELECT * FROM banned_users")
    banned = cursor.fetchall()

    return render_template('admin.html', data=data, banned=banned)


@app.route('/admin', methods=["POST"])
def ban_request():
    user = request.form['user']
    if ban_user(user):
        flash('Ban successful.','success')
        return redirect('/admin')
    else:
        flash('Ban failed.', 'danger')
        return redirect('/admin')



@app.route('/login', methods=["GET", "POST"])
def login_page():
    # TODO: check if the user is in the banned users list
    username = request.form['username']
    password = request.form['password']

    if(ipa_login(username, password)):
        return render_template("home.html")
    else:
        return render_template('login.html')

    if(login_ok[0] == True and login_ok[1] == False):
        print("User: "+username+" loged in, but is not member of: "+get_admin_group())
        return render_template("home.html")
    if(login_ok[0] == True and login_ok[1] == True):
        print("User: "+username+" loged in and is member of: "+get_admin_group())
        return redirect('/admin')
    if(login_ok[0] == False):
        print("User: "+username+" failed login")
        return render_template('login.html')


@app.route('/')
def home():
    return render_template('login.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0')
