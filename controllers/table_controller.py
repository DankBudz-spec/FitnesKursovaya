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

        for col_name, value in zip(cols, row_data):
            val_str = str(value).strip() if value is not None else ""

            nullable_fields = ["phone_secondary", "address", "medical_notes",
                               "photo_path", "last_service_date", "exit_dt", "description"]
            if not val_str and col_name not in nullable_fields:
                return False, f"Поле '{col_name}' обязательно для заполнения!"

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

            if col_name == "email" and val_str:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", val_str):
                    return False, "Введен неверный формат Email адреса!"

            if col_name in ["phone_secondary", "phone_primary", "phone"] and val_str:
                if not re.match(r"^[0-9\+\-\(\)\s]+$", val_str):
                    return False, "Телефон содержит недопустимые буквы или символы!"

            if col_name == "remaining_freeze_days":
                try:
                    if int(val_str) > 30:
                        return False, "Максимальный срок заморозки - 30 дней"
                except ValueError:
                    return False, "Дни заморозки должны быть числом"

        if table_name == "client_subscriptions":
            start_idx = cols.index("start_date")
            end_idx = cols.index("end_date")
            if row_data[end_idx] < row_data[start_idx]:
                return False, "Дата окончания абонемента не может быть раньше даты начала!"

        return True, ""

    def sync_table(self, table_widget, db_table_name, role="Администратор", user_name=""):
        if role == "Тренер" and db_table_name in SQLQueries.TRAINER_QUERIES:
            query = SQLQueries.TRAINER_QUERIES[db_table_name]
            response = self.db.execute_query(query, params=(user_name,), fetch=True)
        else:
            query = SQLQueries.get_select_all(db_table_name)
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

    def mark_client_attended(self, registration_id):
        """Меняет статус записи на 'Посетил'"""
        query = SQLQueries.CONTROLLER_QUERIES["mark_attended"]
        return self.db.execute_query(query, params=(registration_id,), fetch=False)

    def set_equipment_broken(self, equipment_id):
        """Отправляет тренажер в ремонт"""
        query = SQLQueries.CONTROLLER_QUERIES["set_equipment_broken"]
        return self.db.execute_query(query, params=(equipment_id,), fetch=False)

    def get_lookup_data(self, table_name):
        """Возвращает (ID, Название) для ComboBox."""
        query = SQLQueries.get_lookup_query(table_name)
        if not query:
            return []

        response = self.db.execute_query(query, fetch=True)
        return response[0] if response else []

    def add_record(self, table_name, row_data):
        is_valid, error_msg = self.validate_data(table_name, row_data)
        if not is_valid:
            return False, error_msg

        if table_name == "schedule":
            coach_id, start_time, end_time = row_data[1], row_data[3], row_data[4]
            if self.check_schedule_overlap(coach_id, start_time, end_time):
                return False, "У этого тренера уже есть занятие в указанное время! Выберите другое время или тренера."

        query = SQLQueries.get_insert_query(table_name, len(row_data))
        return self.db.execute_query(query, params=row_data, fetch=False)

    def delete_record(self, table_name, record_id):
        query = SQLQueries.get_delete_query(table_name)
        if not query:
            return False
        return self.db.execute_query(query, params=(record_id,), fetch=False)

    def update_record(self, table_name, record_id, row_data):
        is_valid, error_msg = self.validate_data(table_name, row_data)
        if not is_valid:
            return False, error_msg

        if table_name == "schedule":
            coach_id, start_time, end_time = row_data[1], row_data[3], row_data[4]
            if self.check_schedule_overlap(coach_id, start_time, end_time, schedule_id=record_id):
                return False, "У этого тренера уже есть ДРУГОЕ занятие в указанное время!"

        query = SQLQueries.get_update_query(table_name)
        if not query:
            return False

        params = list(row_data) + [record_id]
        return self.db.execute_query(query, params=params, fetch=False)

    def get_record_by_id(self, table_name, record_id, columns="*"):
        query = SQLQueries.get_select_by_id(table_name, columns)
        if not query: return None
        response = self.db.execute_query(query, params=(record_id,), fetch=True)
        if response and response[0] and len(response[0]) > 0:
            return response[0][0]
        return None

    def get_membership_data(self, type_id):
        row = self.get_record_by_id("membership_types", type_id, "duration_days, price")
        if row:
            return {'days': row[0], 'price': row[1]}
        return None

    def get_client_reg_date(self, client_id):
        row = self.get_record_by_id("clients", client_id, "registration_date")
        return row[0] if row else None

    def get_subscription_info(self, sub_id):
        row = self.get_record_by_id("client_subscriptions", sub_id, "client_id, type_id")
        if row:
            return row[0], row[1]
        return None, None

    def freeze_subscription(self, sub_id, days_to_freeze):
        query = SQLQueries.CONTROLLER_QUERIES["get_freeze_info"]
        response = self.db.execute_query(query, params=(sub_id,), fetch=True)

        if not response or not response[0] or len(response[0]) == 0:
            return False, "Абонемент не найден в базе."

        remaining_days, current_end_date = response[0][0]

        if days_to_freeze <= 0:
            return False, "Количество дней должно быть больше нуля."
        if days_to_freeze > remaining_days:
            return False, f"Ошибка: доступно только {remaining_days} дней заморозки."

        new_end_date = current_end_date + timedelta(days=days_to_freeze)
        new_remaining = remaining_days - days_to_freeze

        update_query = SQLQueries.CONTROLLER_QUERIES["update_freeze"]
        success = self.db.execute_query(update_query, params=(new_end_date, new_remaining, sub_id), fetch=False)

        if success:
            return True, f"Успешно заморожено на {days_to_freeze} дн.\nНовая дата окончания: {new_end_date.strftime('%Y-%m-%d')}"
        return False, "Ошибка при обновлении базы данных."

    def get_dashboard_metrics(self):
        metrics = {"active_clients": 0, "debtors": [], "broken_eq": []}

        res_clients = self.db.execute_query(SQLQueries.ANALYTICS_QUERIES["total_active_clients"], fetch=True)
        if res_clients and res_clients[0]:
            metrics["active_clients"] = res_clients[0][0][0]

        res_debtors = self.db.execute_query(SQLQueries.ANALYTICS_QUERIES["debtors"], fetch=True)
        if res_debtors and res_debtors[0]:
            metrics["debtors"] = res_debtors[0]

        res_eq = self.db.execute_query(SQLQueries.ANALYTICS_QUERIES["broken_equipment"], fetch=True)
        if res_eq and res_eq[0]:
            metrics["broken_eq"] = res_eq[0]

        return metrics

    def get_attendance_stats(self):
        query = SQLQueries.ANALYTICS_QUERIES["visits_per_day"]
        res = self.db.execute_query(query, fetch=True)
        return res[0] if res and res[0] else []

    def run_auto_tasks(self):
        query = SQLQueries.ANALYTICS_QUERIES.get("auto_block_debtors")
        if query:
            self.db.execute_query(query, fetch=False)

    def get_chart_data(self, period="week"):
        query_key = f"chart_{period}"
        query = SQLQueries.ANALYTICS_QUERIES.get(query_key)
        if not query: return []
        res = self.db.execute_query(query, fetch=True)
        return res[0] if res and res[0] else []

    def check_schedule_overlap(self, coach_id, start_time, end_time, schedule_id=None):
        params = [coach_id, end_time, start_time]

        if schedule_id:
            query = SQLQueries.CONTROLLER_QUERIES["check_overlap_exclude"]
            params.append(schedule_id)
        else:
            query = SQLQueries.CONTROLLER_QUERIES["check_overlap"]

        res = self.db.execute_query(query, params=tuple(params), fetch=True)
        return True if (res and res[0]) else False

    def translate_error(self, raw_error):
        err = raw_error.lower()
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