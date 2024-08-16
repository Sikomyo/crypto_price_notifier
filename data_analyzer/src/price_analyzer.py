

from components.database.db_setup import DataManagement

class PriceAnalyzer:

    def __init__(self, data_manage_obj):
        self.data_manage_obj = data_manage_obj
    

    def get_analyzed_price(self, symbol: str, username: str, highest: bool):
        conn = self.data_manage_obj.get_db_connection()
        cur = conn.cursor()
        if highest:
            query = '''
            SELECT MAX(price) FROM prices WHERE symbol = %s AND username = %s;
            '''
        else:
            query = '''
            SELECT MIN(price) FROM prices WHERE symbol = %s AND username = %s;
            '''
        cur.execute(query, (symbol,username))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None