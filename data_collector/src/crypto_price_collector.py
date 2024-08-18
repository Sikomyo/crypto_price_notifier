#!/usr/bin/env python3
import requests
import json
import os
import pika


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
            'X-CMC_PRO_API_KEY': 'your_api_key',
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

