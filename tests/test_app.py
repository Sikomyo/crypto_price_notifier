import unittest
from unittest.mock import patch, MagicMock
from basic_server.src.app import app, data_manage_obj, price_analyzer, send_task_to_queue, fetch_and_update_prices

class TestAppRoutes(unittest.TestCase):

    def setUp(self):

        self.app = app.test_client()
        self.app.testing = True


    @patch('basic_server.src.app.data_manage_obj.get_db_connection')
    def test_main_route(self, mock_db_conn):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)
    

    @patch('basic_server.src.app.data_manage_obj.get_db_connection')
    def test_login_route_get(self, mock_db_conn):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)


    @patch('basic_server.src.app.data_manage_obj.get_db_connection')
    def test_login_route_post_success(self, mock_db_conn):
        # Mocking database cursor and connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = ('password123',)

        mock_db_conn.return_value = mock_conn

        response = self.app.post('/login', data={'username': 'user1', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)  # Redirect


    @patch('basic_server.src.app.data_manage_obj.get_db_connection')
    def test_register_route_post_success(self, mock_db_conn):
        # Mocking database cursor and connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        mock_db_conn.return_value = mock_conn

        response = self.app.post('/register', data={'username': 'new_user', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)  # Redirect


    @patch('basic_server.src.app.pika.BlockingConnection')
    def test_send_task_to_queue(self, mock_blocking_connection):
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_blocking_connection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        
        task_data = {"username": "user1", "symbol": "BTC"}
        send_task_to_queue(task_data)
        
        mock_channel.queue_declare.assert_called_once_with(queue='price_update', durable=True)
        mock_channel.basic_publish.assert_called_once()
        mock_connection.close.assert_called_once()


    @patch('basic_server.src.app.send_task_to_queue')
    @patch('basic_server.src.app.data_manage_obj.get_db_connection')
    def test_fetch_and_update_prices(self, mock_db_conn, mock_send_task):

        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchall.return_value = [('user1', 'BTC')]

        mock_db_conn.return_value = mock_conn

        fetch_and_update_prices()
        
        mock_send_task.assert_called_once_with(
            {"username": "user1", "symbol": "BTC"},
            queue_name='price_update'
        )
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


