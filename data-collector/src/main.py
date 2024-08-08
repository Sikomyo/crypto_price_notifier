#!/usr/bin/env python3
from crypto_price_collector import CryptoDataCollector

class Main:

    def run(crypto_symbol):
        crypto_symbol = crypto_symbol

        crypto_data_object = CryptoDataCollector()
        latest_crypto_price, time = crypto_data_object.get_crypto_price(crypto_symbol)
        print(f"{crypto_symbol} Price: {latest_crypto_price}, Time: {time}")
        

if __name__ == "__main__":
    Main.run('BTC')