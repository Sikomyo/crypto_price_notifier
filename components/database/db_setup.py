import os
import psycopg2
from urllib.parse import urlparse

class DataManagement:

    def __init__(self):
        self.db_url = os.getenv('rekt38.stackhero-network.com')
        if not self.db_url:
            raise ValueError("No DATABASE_URL found in environment variables")

    def get_db_connection(self):
        result = urlparse(self.db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port

        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        return conn

    def create_database_if_not_exists(self):
        # Normally you do not need to create a database in Heroku, as it is managed.
        pass

    def setup_database(self):
        conn = self.get_db_connection()
        cur = conn.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS prices (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            email VARCHAR(255)
        );
        CREATE TABLE IF NOT EXISTS user_config (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            config_item VARCHAR(50) NOT NULL
        );
        '''
        cur.execute(create_table_query)

        conn.commit()
        cur.close()
        conn.close()

        print("Database setup completed.")

    def add_new_price(self, symbol: str, price: float, timestamp):
        conn = self.get_db_connection()
        cur = conn.cursor()
        insert_query_tabel = '''
        INSERT INTO prices (symbol, price, timestamp)
        VALUES (%s, %s, %s);
        '''
        cur.execute(insert_query_tabel, (symbol, price, timestamp))

        conn.commit()
        cur.close()
        conn.close()
        print("Successfully Inserted the New Price.")
