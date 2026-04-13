from PyQt6.QtWidgets import QTableWidgetItem
from database.db_manager import DBManager
from database.queries import SQLQueries


class TableController:
    def __init__(self):
        self.db = DBManager()

    def sync_table(self, table_widget, db_table_name):
        query = SQLQueries.get_select_all(db_table_name)
        if not query:
            return

        response = self.db.execute_query(query, fetch=True)

        if response is None:
            return

        data, _ = response

        table_widget.setRowCount(0)

        for row_number, row_data in enumerate(data):
            table_widget.insertRow(row_number)
            for column_number, value in enumerate(row_data):
                text_value = str(value) if value is not None else ""
                item = QTableWidgetItem(text_value)
                table_widget.setItem(row_number, column_number, item)

    def get_lookup_data(self, table_name):
        """Возвращает список (ID, Название) для выпадающих списков"""
        from database.queries import SQLQueries
        info = SQLQueries.TABLES.get(table_name)
        if not info: return []

        display_col = info.get("display_col", info["id"])
        query = f"SELECT {info['id']}, {display_col} FROM {table_name} ORDER BY {display_col};"

        result, _ = self.db.execute_query(query, fetch=True)
        return result if result else []

    def add_record(self, table_name, row_data):
        query = SQLQueries.get_insert_query(table_name, len(row_data))

        return self.db.execute_query(query, params=row_data, fetch=False)

    def delete_record(self, table_name, record_id):
        query = SQLQueries.get_delete_query(table_name)
        if not query:
            return False

        return self.db.execute_query(query, params=(record_id,), fetch=False)

    def update_record(self, table_name, record_id, row_data):
        query = SQLQueries.get_update_query(table_name)
        if not query:
            return False

        # Формируем список параметров: сначала новые данные, потом ID для WHERE
        params = list(row_data) + [record_id]
        return self.db.execute_query(query, params=params, fetch=False)

    def translate_error(self, raw_error):
        """Переводит технические ошибки БД на человеческий русский"""
        err = raw_error.lower()

        # Словарь соответствий: имя ограничения -> понятный текст
        translations = {
            "check_age": "Клиент должен быть старше 14 лет!",
            "check_price": "Цена должна быть больше нуля!",
            "check_dates": "Дата окончания не может быть раньше даты начала!",
            "phone_primary_key": "Этот номер телефона уже занят!",
            "email_key": "Этот Email уже зарегистрирован!",
            "is_blocked": "Поле 'Заблокирован' должно быть 0 или 1!",
            "not-null": "Все обязательные поля должны быть заполнены!",
            "foreign key": "Нельзя удалить или изменить запись, так как она используется в других таблицах."
        }

        for key, value in translations.items():
            if key in err:
                return value

        return raw_error
