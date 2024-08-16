#!/usr/bin/env python3

import sys
import os
import atexit
from flask import Flask, request, redirect, url_for, session, render_template_string
from threading import Thread
from .config import ITEMS as cryto_list
from data_analyzer.src.price_analyzer import PriceAnalyzer
from data_collector.src.crypto_price_collector import CryptoDataCollector
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from components.database.db_setup import DataManagement


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_TYPE'] = 'filesystem'

data_manage_obj = DataManagement()
data_manage_obj.setup_database()
price_analyzer = PriceAnalyzer(data_manage_obj)


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
        
        cur.execute("SELECT email, minutely, hourly, daily FROM users WHERE username = %s", (username,))
        user_info = cur.fetchone()
        user_email = user_info[0] if user_info else ''
        minutely = user_info[1] if user_info else False
        hourly = user_info[2] if user_info else False
        daily = user_info[3] if user_info else False
        
        latest_prices = {
            item: price_analyzer.get_analyzed_price(symbol=item, username=username, highest=False)
            for item in selected_items
        }
        
        cur.close()
        conn.close()
        
        items_checkboxes = ''.join([
            f'<input type="checkbox" name="config_item" value="{item}" {"checked" if item in selected_items else ""}>{item} - Latest Price: {latest_prices.get(item, "N/A")}<br>'
            for item in cryto_list
        ])
        
        return f'''
        <h2>Configuration Page</h2>
        <p>Welcome, {username}!</p>
        <form method="POST" action="/logout">
            <input type="submit" value="Logout">
        </form>
        <h4>Settings</h4>
        <form method="POST" action="/save_config">
            Email: <input type="text" name="email" value="{user_email}"><br><br>
            <label for="config_item">Choose items:</label><br>
            {items_checkboxes}
            <h4>Get Prices</h4>
            <input type="checkbox" id="minutely" name="minutely" value="True" {"checked" if minutely else ""}>
            <label for="minutely">Minutely</label><br>
            <input type="checkbox" id="hourly" name="hourly" value="True" {"checked" if hourly else ""}>
            <label for="hourly">Hourly</label><br>
            <input type="checkbox" id="daily" name="daily" value="True" {"checked" if daily else ""}>
            <label for="daily">Daily</label><br>
            <br>
            <input type="submit" value="Save">
        </form>
        <a href="/check_price"><h4>Prices Report</h4></a>
        '''
    return redirect(url_for("login"))



@app.route("/save_config", methods=["POST"])
def save_config():
    if 'username' in session:
        username = session['username']
        selected_items = request.form.getlist("config_item")
        email = request.form.get("email")
        
        # Determine if checkboxes are checked
        minutely = 'minutely' in request.form
        hourly = 'hourly' in request.form
        daily = 'daily' in request.form
        
        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()
        
        # Update email and schedule preferences
        cur.execute(
            "UPDATE users SET email = %s, minutely = %s, hourly = %s, daily = %s WHERE username = %s", 
            (email, minutely, hourly, daily, username)
        )
        
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


@app.route("/check_price", methods=["GET"])
def check_price():
    if 'username' in session:
        username = session['username']
        
        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()
        
        # Fetch user's selected items from the user_config table
        cur.execute("SELECT config_item FROM user_config WHERE username = %s", (username,))
        selected_items = cur.fetchall()
        selected_items = [item[0] for item in selected_items]

        # Fetch highest and lowest prices for each selected item
        prices_info = []
        for item in selected_items:
            highest_price = price_analyzer.get_analyzed_price(symbol=item, username=username, highest=True)
            lowest_price = price_analyzer.get_analyzed_price(symbol=item, username=username, highest=False)
            prices_info.append({'symbol': item, 'highest': highest_price, 'lowest': lowest_price})
        
        cur.close()
        conn.close()

        return render_template_string('''
        <h2>Today Price Report</h2>
        {% for price in prices_info %}
            <h3>{{ price.symbol }}</h3>
            <p>Highest Price Today: {{ price.highest }}</p>
            <p>Lowest Price Today: {{ price.lowest }}</p>
        {% endfor %}
        <a href="/config">Go back</a>
        ''', prices_info=prices_info)

    return redirect(url_for("login"))


def start_consumer():
    data_manage_obj.consume_from_queue()


def fetch_and_update_prices():
    print("It is inside fetch and update price")
    conn = data_manage_obj.get_db_connection()
    cur = conn.cursor()
    crypto_data_collector = CryptoDataCollector()
    # Get the list of users with their selected items
    cur.execute("""
        SELECT uc.username, uc.config_item 
        FROM user_config uc
        JOIN users u ON uc.username = u.username 
        WHERE u.minutely = true OR u.hourly = true OR u.daily = true
    """)
    user_items = cur.fetchall()

    for username, symbol in user_items:
        # Fetch the price for each selected item
        crypto_price, timestamp = crypto_data_collector.get_crypto_price(symbol=symbol)
        
        if crypto_price and timestamp:
            # Save the data to the prices table
            cur.execute("""
                INSERT INTO prices (symbol, price, timestamp, username)
                VALUES (%s, %s, %s, %s)
            """, (symbol, crypto_price, timestamp, username))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Fetched and updated prices at {datetime.now()}")


def initialize_scheduler():
    print("Inside initialize scheduler")
    scheduler = BackgroundScheduler()

    conn = data_manage_obj.get_db_connection()
    cur = conn.cursor()

    # Fetch users with their scheduling preferences
    cur.execute("""
        SELECT username, minutely, hourly, daily 
        FROM users
    """)
    users = cur.fetchall()

    for username, minutely, hourly, daily in users:
        if minutely:
            scheduler.add_job(func=fetch_and_update_prices, trigger="interval", minutes=1, id=f"{username}_minutely")
        if hourly:
            scheduler.add_job(func=fetch_and_update_prices, trigger="interval", hours=1, id=f"{username}_hourly")
        if daily:
            scheduler.add_job(func=fetch_and_update_prices, trigger="interval", days=1, id=f"{username}_daily")

    cur.close()
    conn.close()

    # Start the scheduler
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    initialize_scheduler()
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.start()
    app.run(debug=True)
