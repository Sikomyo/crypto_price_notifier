#!/usr/bin/env python3
import requests
import json
import os
import ssl
import pika
from components.database.db_setup import DataManagement
from datetime import datetime


class CryptoDataCollector:

    def __init__(self):
        self.rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')
        self.rabbitmq_queue = os.getenv('RABBITMQ_QUEUE', 'crypto_prices')
        self.rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
        self.rabbitmq_pass = os.getenv('RABBITMQ_PASS', 'guest')


    def get_crypto_price(self, symbol: str):
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
            'symbol': symbol,
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '3b3e4dcc-660a-410c-8f92-8cc888391327',  # replace with your actual API key
        }

        try:
            response = requests.get(url, headers=headers, params=parameters)
            data = response.json()

            if response.status_code == 200:
                crypto_price = round(data['data'][symbol]['quote']['USD']['price'], 2)
                timestamp = data['data'][symbol]['last_updated']
                return crypto_price, timestamp
            else:
                print(f"Error {response.status_code}: {data['status']['error_message']}")
                return None, None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None


    def send_to_queue(self, message):
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbitmq_host, port=self.rabbitmq_port, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=self.rabbitmq_queue)
        channel.basic_publish(exchange='', routing_key=self.rabbitmq_queue, body=json.dumps(message))
        connection.close()


    def collect_and_send(self, symbol: str):
        price, timestamp = self.get_crypto_price(symbol)
        message = {'symbol': symbol, 'price': price, 'timestamp': timestamp}
        self.send_to_queue(message)


    def fetch_and_save_price(self, task):
        username = task['username']
        symbol = task['symbol']

        data_manage_obj = DataManagement()
        conn = data_manage_obj.get_db_connection()
        cur = conn.cursor()

        try:
            # Fetch the price for each selected item
            crypto_price, timestamp = self.get_crypto_price(symbol=symbol)
            
            if crypto_price and timestamp:
                # Save the data to the prices table
                cur.execute("""
                    INSERT INTO prices (symbol, price, timestamp, username)
                    VALUES (%s, %s, %s, %s)
                """, (symbol, crypto_price, timestamp, username))
                conn.commit()
                print(f"Fetched and saved price for {symbol} at {datetime.now()}")
            else:
                print(f"Failed to fetch price for {symbol}.")
        finally:
            cur.close()
            conn.close()



    def start_price_update_consumer(self, queue_name='price_update'):
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_pass)
        ssl_options = pika.SSLOptions(ssl.create_default_context(), self.rabbitmq_host)

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host, port=self.rabbitmq_port, 
                                                                       credentials=credentials ,ssl_options=ssl_options))
        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue=queue_name, durable=True)

        def callback(ch, method, properties, body):
            task = json.loads(body)
            print(f"Received task: {task}")
            # Process the task here
            self.fetch_and_save_price(task)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        # Consume messages
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        print(f" [*] Waiting for messages in {queue_name}. To exit press CTRL+C")
        channel.start_consuming()


if __name__ == "__main__":
    collector = CryptoDataCollector()
    collector.start_price_update_consumer()
