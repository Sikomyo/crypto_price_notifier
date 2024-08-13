import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class DataManagement:

    def __init__(self):
        self.host = os.getenv('STACKHERO_POSTGRESQL_HOST', 'localhost')
        self.port = os.getenv('STACKHERO_POSTGRESQL_PORT', '5432')
        self.admin_password = os.getenv('STACKHERO_POSTGRESQL_ADMIN_PASSWORD', 'pass12345')
        self.database = os.getenv('DATABASE_NAME', 'project_db')
        self.user = os.getenv('DATABASE_USER', 'postgres')
        
        if not self.host or not self.port or not self.admin_password:
            raise ValueError("One or more of the required environment variables are missing")

        self.db_url = f"postgresql://{self.user}:{self.admin_password}@{self.host}:{self.port}/{self.database}"

    def get_db_connection(self):
        result = urlparse(self.db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port

        sslmode = 'require' if hostname != 'localhost' else 'disable'

        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode=sslmode  # Adjust SSL mode based on the hostname
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
