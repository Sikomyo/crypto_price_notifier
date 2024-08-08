#!/usr/bin/env python3
import requests
import json

class CryptoDataCollector:

    def __init__(self):
        pass


    def get_crypto_price(self, symbol: str):

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {
        'symbol':symbol,
        }
        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '3b3e4dcc-660a-410c-8f92-8cc888391327',
        }

        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()
        response = requests.get(url, headers=headers, params=parameters)
        data = response.json()

        if response.status_code == 200:
            crypto_price = round(data['data'][symbol]['quote']['USD']['price'], 2)
            timestamp = data['data'][symbol]['last_updated']
            return crypto_price, timestamp
        else:
            print(f"Error {response.status_code}: {data['status']['error_message']}")
            return None

