import psycopg2
from config import DB_CONFIG


class DBManager:
    def __init__(self):
        self.params = DB_CONFIG

    def _get_connection(self):
        return psycopg2.connect(**self.params)

    def execute_query(self, query, params=None, fetch=False):
        conn = None
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return result, "Успешно"

                conn.commit()
                return True, "Операция выполнена успешно"
        except Exception as e:
            if conn: conn.rollback()
            # Возвращаем False и сам текст ошибки из базы данных
            error_msg = str(e).split('\n')[0]  # Берем только первую строку ошибки
            return False, error_msg
        finally:
            if conn: conn.close()