import unittest
from unittest.mock import patch, MagicMock
from data_collector.src.crypto_price_collector import CryptoDataCollector

class TestCryptoPriceCollector(unittest.TestCase):


    def setUp(self):
        self.collector = CryptoDataCollector()


    @patch('data_collector.src.crypto_price_collector.requests.get')
    def test_get_crypto_price_success(self, mock_get):
        # Arrange
        mock_response = MagicMock()
        expected_price = 30000.00
        expected_timestamp = '2024-08-18T12:00:00Z'
        mock_response.json.return_value = {
            'data': {
                'BTC': {
                    'quote': {
                        'USD': {
                            'price': expected_price
                        }
                    },
                    'last_updated': expected_timestamp
                }
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        price, timestamp = self.collector.get_crypto_price('BTC')

        self.assertEqual(price, expected_price)
        self.assertEqual(timestamp, expected_timestamp)


    @patch('data_collector.src.crypto_price_collector.requests.get')
    def test_get_crypto_price_failure(self, mock_get):
       
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'status': {'error_message': 'Internal Server Error'}}
        mock_get.return_value = mock_response

        price, timestamp = self.collector.get_crypto_price('BTC')

        self.assertIsNone(price)
        self.assertIsNone(timestamp)


    def test_get_crypto_price_integration(self):
        
        symbol = 'BTC'
        price, timestamp = self.collector.get_crypto_price(symbol)
       
        self.assertIsNotNone(price)
        self.assertIsNotNone(timestamp)


    @patch('data_collector.src.crypto_price_collector.DataManagement')
    @patch('data_collector.src.crypto_price_collector.CryptoDataCollector.get_crypto_price')
    def test_fetch_and_save_price_failure(self, mock_get_crypto_price, mock_data_management):
        mock_get_crypto_price.return_value = (None, None)
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_data_management.return_value.get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        task = {
            'username': 'test_user',
            'symbol': 'BTC'
        }

        self.collector.fetch_and_save_price(task)

        mock_cur.execute.assert_not_called()
        mock_conn.commit.assert_not_called()
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
