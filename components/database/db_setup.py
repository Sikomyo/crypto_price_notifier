#!/usr/bin/env python3

# Database connection details
# DB_NAME = 'project_db'
# DB_USER = 'postgres'
# DB_PASS = 'pass12345'
# DB_HOST = 'localhost'
# DB_PORT = '5432'


import psycopg2
from psycopg2 import sql

class DataManagement:

    def __init__(self, db_name, db_user, db_pass, db_host, db_port):
        self.DB_NAME = db_name
        self.DB_USER = db_user
        self.DB_PASS = db_pass
        self.DB_HOST = db_host
        self.DB_PORT = db_port


    def create_database_if_not_exists(self):
        conn = psycopg2.connect(
            dbname='postgres', 
            user=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Check if database exists
        cur.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), [self.DB_NAME])
        exists = cur.fetchone()
        if not exists:
            # Create database if it does not exist
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.DB_NAME)))
            print(f"Database {self.DB_NAME} created.")
        else:
            print(f"Database {self.DB_NAME} already exists.")

        cur.close()
        conn.close()


    def get_db_connection(self):
        conn = psycopg2.connect(
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT
        )
        return conn
    

    def setup_database(self):

        conn = self.get_db_connection()
        cur = conn.cursor()

        # Create table if it does not exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            email VARCHAR(255)
        );
        '''
        create_config_table = '''
        CREATE TABLE IF NOT EXISTS user_config (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        config_item VARCHAR(50) NOT NULL
        );
        '''
        cur.execute(create_table_query)
        cur.execute(create_config_table)
        conn.commit()
        cur.close()
        conn.close()
        print("Users table, and Config Table are created successfully.")


    # def create_users_table(self):
    #     conn = self.get_db_connection()
    #     cur = conn.cursor()
    #     create_table_query = '''
    #     CREATE TABLE IF NOT EXISTS users (
    #         id SERIAL PRIMARY KEY,
    #         username VARCHAR(50) UNIQUE NOT NULL,
    #         password VARCHAR(50) NOT NULL
    #     );
    #     '''
    #     create_config_table = '''
    #     CREATE TABLE user_config (
    #     id SERIAL PRIMARY KEY,
    #     username VARCHAR(50) NOT NULL,
    #     config_item VARCHAR(50) NOT NULL
    #     );
    #     '''
    #     cur.execute(create_table_query)
    #     cur.execute(create_config_table)
    #     conn.commit()
    #     cur.close()
    #     conn.close()
    #     print("Users table created successfully.")


    def add_new_price(self, symbol: str, price: float, timestamp):

        conn = psycopg2.connect(
            dbname=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASS,
            host=self.DB_HOST,
            port=self.DB_PORT
        )
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
