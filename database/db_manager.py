import psycopg2
from config import DB_CONFIG


class DBManager:
    def __init__(self):
        self.params = DB_CONFIG

    def _get_connection(self):
        return psycopg2.connect(**self.params)

    def execute_query(self, query, params=None, fetch=False):
        """
        Универсальный метод для выполнения SQL.
        fetch=True — если нужно вернуть данные (SELECT).
        fetch=False — если нужно просто выполнить (INSERT/DELETE).
        """
        conn = None
        result = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    colnames = [desc[0] for desc in cursor.description]
                    return result, colnames
                conn.commit()
        except Exception as e:
            print(f"Database Error: {e}")
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
        return result