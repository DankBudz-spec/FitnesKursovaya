from PyQt6.QtWidgets import QTableWidgetItem
from database.db_manager import DBManager
from database.queries import SQLQueries
import hashlib
from datetime import timedelta
import re


class TableController:
    def __init__(self):
        self.db = DBManager()

    def _hash_password(self, password):
        """Превращает пароль в нечитаемый хэш"""
        if not password: return None
        # Используем алгоритм SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_data(self, table_name, row_data):
        """
        Программная реализация ограничений доменной целостности.
        Проверяет данные ДО отправки в базу.
        """
        table_info = SQLQueries.TABLES.get(table_name)
        if not table_info:
            return True, ""

        cols = table_info["cols"]

        # Проходим по всем переданным значениям и их названиям колонок
        for col_name, value in zip(cols, row_data):
            val_str = str(value).strip() if value is not None else ""

            # 1. Проверка на запрет пустых значений (NOT NULL ограничение)
            # Список полей, которым разрешено быть пустыми (NULL)
            nullable_fields = ["phone_secondary", "address", "medical_notes",
                               "photo_path", "last_service_date", "exit_dt", "description"]
            if not val_str and col_name not in nullable_fields:
                return False, f"Поле '{col_name}' обязательно для заполнения!"

            # 2. Доменная целостность: проверка чисел
            if col_name in ["price", "amount", "salary_rate"]:
                try:
                    if float(val_str) <= 0:
                        return False, "Сумма или ставка должна быть строго больше нуля!"
                except ValueError:
                    return False, "Введено некорректное число."

            if col_name == "capacity":
                try:
                    if int(val_str) <= 0:
                        return False, "Вместимость должна быть положительным целым числом!"
                except ValueError:
                    return False, "Вместимость должна быть числом."

            # 3. Доменная целостность: форматы данных (Email)
            if col_name == "email" and val_str:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", val_str):
                    return False, "Введен неверный формат Email адреса!"

            # 4. Проверка телефона (только цифры и базовые символы связи)
            if col_name in ["phone_secondary", "phone_primary", "phone"] and val_str:
                if not re.match(r"^[0-9\+\-\(\)\s]+$", val_str):
                    return False, "Телефон содержит недопустимые буквы или символы!"

        # 5. Комплексные проверки целостности (Сравнение дат)
        if table_name == "client_subscriptions":
            start_idx = cols.index("start_date")
            end_idx = cols.index("end_date")
            if row_data[end_idx] < row_data[start_idx]:
                return False, "Дата окончания абонемента не может быть раньше даты начала!"

        return True, ""

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
        """Возвращает (ID, Название) для ComboBox. Для клиентов добавляет телефон."""
        info = SQLQueries.TABLES.get(table_name)
        if not info: return []

        display_col = info.get("display_col", info["id"])

        # Специфическая логика для вывода клиентов: ФИО | Телефон
        if table_name == "clients":
            query = f"SELECT client_id, (full_name || ' | ' || phone_primary) FROM clients ORDER BY full_name;"
        elif table_name == "staff":
            query = f"SELECT staff_id, (full_name || ' | ' || position) FROM staff ORDER BY full_name;"
        elif table_name == "schedule":
            # Для выбора записи в расписании показываем занятие + время
            query = """
                SELECT sch.schedule_id, (cl.name || ' | ' || sch.start_time) 
                FROM schedule sch 
                JOIN classes cl ON sch.class_type_id = cl.class_type_id 
                ORDER BY sch.start_time;
            """
        else:
            query = f"SELECT {info['id']}, {display_col} FROM {table_name} ORDER BY {display_col};"

        response = self.db.execute_query(query, fetch=True)
        return response[0] if response else []

    def add_record(self, table_name, row_data):
        # ВНЕДРЯЕМ ПРОВЕРКУ ПЕРЕД ЗАПРОСОМ
        is_valid, error_msg = self.validate_data(table_name, row_data)
        if not is_valid:
            return False, error_msg  # Возвращаем ошибку валидации

        query = SQLQueries.get_insert_query(table_name, len(row_data))
        return self.db.execute_query(query, params=row_data, fetch=False)

    def delete_record(self, table_name, record_id):
        query = SQLQueries.get_delete_query(table_name)
        if not query:
            return False

        return self.db.execute_query(query, params=(record_id,), fetch=False)

    def update_record(self, table_name, record_id, row_data):
        # ВНЕДРЯЕМ ПРОВЕРКУ ПЕРЕД ЗАПРОСОМ
        is_valid, error_msg = self.validate_data(table_name, row_data)
        if not is_valid:
            return False, error_msg

        query = SQLQueries.get_update_query(table_name)
        if not query:
            return False

        params = list(row_data) + [record_id]
        return self.db.execute_query(query, params=params, fetch=False)

    def get_record_by_id(self, table_name, record_id, columns="*"):
        """Базовый метод: безопасно достает данные из БД"""
        query = SQLQueries.get_select_by_id(table_name, columns)
        if not query: return None

        response = self.db.execute_query(query, params=(record_id,), fetch=True)
        if response and response[0] and len(response[0]) > 0:
            return response[0][0]  # Возвращает кортеж с данными строки
        return None

    def get_membership_data(self, type_id):
        """Инфо о тарифе"""
        row = self.get_record_by_id("membership_types", type_id, "duration_days, price")
        if row:
            return {'days': row[0], 'price': row[1]}
        return None

    def get_client_reg_date(self, client_id):
        """Дата регистрации клиента"""
        row = self.get_record_by_id("clients", client_id, "registration_date")
        return row[0] if row else None

    def get_subscription_info(self, sub_id):
        """Достает ID клиента и ID тарифа из абонемента"""
        row = self.get_record_by_id("client_subscriptions", sub_id, "client_id, type_id")
        if row:
            return row[0], row[1]
        return None, None

    def freeze_subscription(self, sub_id, days_to_freeze):
        """Замораживает абонемент: сдвигает end_date и уменьшает remaining_freeze_days"""
        # Достаем текущие значения
        query = "SELECT remaining_freeze_days, end_date FROM client_subscriptions WHERE subscription_id = %s;"
        response = self.db.execute_query(query, params=(sub_id,), fetch=True)

        if not response or not response[0] or len(response[0]) == 0:
            return False, "Абонемент не найден в базе."

        remaining_days, current_end_date = response[0][0]

        if days_to_freeze <= 0:
            return False, "Количество дней должно быть больше нуля."

        if days_to_freeze > remaining_days:
            return False, f"Ошибка: доступно только {remaining_days} дней заморозки."

        # Считаем новые значения
        new_end_date = current_end_date + timedelta(days=days_to_freeze)
        new_remaining = remaining_days - days_to_freeze

        # Обновляем базу данных
        update_query = """
            UPDATE client_subscriptions 
            SET end_date = %s, remaining_freeze_days = %s 
            WHERE subscription_id = %s;
        """
        success = self.db.execute_query(update_query, params=(new_end_date, new_remaining, sub_id), fetch=False)

        if success:
            return True, f"Успешно заморожено на {days_to_freeze} дн.\nНовая дата окончания: {new_end_date.strftime('%Y-%m-%d')}"
        return False, "Ошибка при обновлении базы данных."

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
            "foreign key": "Нельзя удалить или изменить запись, так как она используется в других таблицах.",
            "invalid": "Введен неверный формат данных"
        }

        for key, value in translations.items():
            if key in err:
                return value

        return raw_error
