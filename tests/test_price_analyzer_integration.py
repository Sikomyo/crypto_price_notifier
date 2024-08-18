import unittest
from data_analyzer.src.price_analyzer import PriceAnalyzer
from components.database.db_setup import DataManagement
from datetime import datetime
import psycopg2

class TestPriceAnalyzerIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
 
        cls.data_manage_obj = DataManagement()
        cls.conn = cls.data_manage_obj.get_db_connection()
        cls.cur = cls.conn.cursor()
        cls.analyzer = PriceAnalyzer(cls.data_manage_obj)

        # Create the prices table for testing
        cls.cur.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10),
                price DECIMAL(10, 2),
                timestamp TIMESTAMP,
                username VARCHAR(50)
            );
        ''')
        cls.conn.commit()


    def setUp(self):

        self.test_date = datetime(2024, 8, 18).date()
        self.cur.execute('''
            INSERT INTO prices (symbol, price, timestamp, username)
            VALUES 
            ('BTC', 35000.00, %s, 'test_user'),
            ('BTC', 30000.00, %s, 'test_user');
        ''', (self.test_date, self.test_date))
        self.conn.commit()


    def tearDown(self):

        self.cur.execute('DELETE FROM prices;')
        self.conn.commit()


    def test_get_analyzed_price_highest(self):

        result = self.analyzer.get_analyzed_price(symbol='BTC', username='test_user', highest=True)

        self.assertEqual(result, 35000.00)


    def test_get_analyzed_price_lowest(self):

        result = self.analyzer.get_analyzed_price(symbol='BTC', username='test_user', highest=False)


        self.assertEqual(result, 30000.00)


    def test_get_analyzed_price_no_data(self):

        result = self.analyzer.get_analyzed_price(symbol='ETH', username='test_user', highest=True)


        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
