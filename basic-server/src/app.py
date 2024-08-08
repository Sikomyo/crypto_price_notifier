#!/usr/bin/env python3

import sys
import os
from flask import Flask, request, redirect, url_for, session
import psycopg2
from .config import ITEMS as cryto_list

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from components.database.db_setup import DataManagement


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_TYPE'] = 'filesystem'

# Database connection details
DB_NAME = 'project_db'
DB_USER = 'postgres'
DB_PASS = 'pass12345'
DB_HOST = 'localhost'
DB_PORT = '5432'

data_manage_obj = DataManagement(db_name=DB_NAME, db_user=DB_USER, db_pass=DB_PASS, db_host=DB_HOST, db_port=DB_PORT)
data_manage_obj.create_database_if_not_exists()
data_manage_obj.setup_database()


@app.route("/")
def main():
    return '''
    <h1>Welcome</h1>
    <h2>Crypto Price Notifier</h2>
    <a href="/login">Login</a> | <a href="/register">Register</a>
    '''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and result[0] == password:
            session['username'] = username
            return redirect(url_for("config"))
        return "Invalid credentials, please try again."
    return '''
    <h2>Login</h2>
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        result = cur.fetchone()

        if result:
            cur.close()
            conn.close()
            return "Username already exists, please choose another."

        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("login"))
    return '''
    <h2>Register</h2>
    <form method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Register">
    </form>
    '''

@app.route("/config")
def config():
    if 'username' in session:
        username = session['username']
        
        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()
        
        # Fetch previously selected items and email
        cur.execute("SELECT config_item FROM user_config WHERE username = %s", (username,))
        selected_items = cur.fetchall()
        selected_items = [item[0] for item in selected_items]
        
        cur.execute("SELECT email FROM users WHERE username = %s", (username,))
        user_email = cur.fetchone()
        user_email = user_email[0] if user_email else ''
        
        cur.close()
        conn.close()
        
        items_checkboxes = ''.join([
            f'<input type="checkbox" name="config_item" value="{item}" {"checked" if item in selected_items else ""}>{item}<br>'
            for item in cryto_list
        ])
        
        return f'''
        <h2>Configuration Page</h2>
        <p>Welcome, {username}!</p>
        <form method="POST" action="/logout">
            <input type="submit" value="Logout">
        </form>
        <h3>Configuration Settings</h3>
        <form method="POST" action="/save_config">
            Email to get notification: <input type="text" name="email" value="{user_email}"><br><br>
            <label for="config_item">Choose items:</label><br>
            {items_checkboxes}
            <input type="submit" value="Save">
        </form>
        '''
    return redirect(url_for("login"))

@app.route("/save_config", methods=["POST"])
def save_config():
    if 'username' in session:
        username = session['username']
        selected_items = request.form.getlist("config_item")
        email = request.form.get("email")
        
        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()
        
        # Update email
        cur.execute("UPDATE users SET email = %s WHERE username = %s", (email, username))
        
        # Clear previous selections
        cur.execute("DELETE FROM user_config WHERE username = %s", (username,))
        
        # Insert new selections
        for item in selected_items:
            cur.execute("INSERT INTO user_config (username, config_item) VALUES (%s, %s)", (username, item))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return f"Configuration saved: {', '.join(selected_items)}"
    return redirect(url_for("login"))


@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))

# if __name__ == "__main__":
#     app.run(debug=True)
