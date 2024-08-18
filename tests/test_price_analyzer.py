import unittest
from unittest.mock import patch, MagicMock
from data_analyzer.src.price_analyzer import PriceAnalyzer
from datetime import datetime

class TestPriceAnalyzer(unittest.TestCase):

    def setUp(self):
        self.data_manage_obj = MagicMock()
        self.analyzer = PriceAnalyzer(self.data_manage_obj)


    @patch('data_analyzer.src.price_analyzer.datetime')
    def test_get_analyzed_price_highest(self, mock_datetime):

        mock_datetime.now.return_value = datetime(2024, 8, 18)
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        self.data_manage_obj.get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (35000.00,)  # Mocked highest price

        result = self.analyzer.get_analyzed_price(symbol='BTC', username='test_user', highest=True)

        mock_cur.execute.assert_called_once_with(
            '''
            SELECT MAX(price) FROM prices 
            WHERE symbol = %s AND username = %s AND DATE(timestamp) = %s;
            ''',
            ('BTC', 'test_user', mock_datetime.now.return_value.date())
        )
        self.assertEqual(result, 35000.00)

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


    @patch('data_analyzer.src.price_analyzer.datetime')
    def test_get_analyzed_price_lowest(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 8, 18)
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        self.data_manage_obj.get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = (30000.00,)  # Mocked lowest price

        result = self.analyzer.get_analyzed_price(symbol='BTC', username='test_user', highest=False)

        mock_cur.execute.assert_called_once_with(
            '''
            SELECT MIN(price) FROM prices 
            WHERE symbol = %s AND username = %s AND DATE(timestamp) = %s;
            ''',
            ('BTC', 'test_user', mock_datetime.now.return_value.date())
        )
        self.assertEqual(result, 30000.00)

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


    @patch('data_analyzer.src.price_analyzer.datetime')
    def test_get_analyzed_price_no_data(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 8, 18)
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        self.data_manage_obj.get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None  # Mocked no data

        result = self.analyzer.get_analyzed_price(symbol='BTC', username='test_user', highest=True)

        mock_cur.execute.assert_called_once_with(
            '''
            SELECT MAX(price) FROM prices 
            WHERE symbol = %s AND username = %s AND DATE(timestamp) = %s;
            ''',
            ('BTC', 'test_user', mock_datetime.now.return_value.date())
        )
        self.assertIsNone(result)

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
