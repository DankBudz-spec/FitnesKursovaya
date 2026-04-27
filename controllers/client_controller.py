from database.db_manager import DBManager
from database.queries import SQLQueries

class ClientLogicController:
    def __init__(self):
        self.db = DBManager() # Исправлено: добавлены скобки!

    # --- МЕТОДЫ ПОЛУЧЕНИЯ ДАННЫХ ДЛЯ ИНТЕРФЕЙСА ---
    def get_profile_info(self, client_id):
        query = SQLQueries.CLIENT_QUERIES["profile"]
        res = self.db.execute_query(query, (client_id,), fetch=True)
        return res[0][0] if res and res[0] else None

    def get_available_schedule(self):
        query = SQLQueries.CLIENT_QUERIES["available_schedule"]
        res = self.db.execute_query(query, fetch=True)
        return res[0] if res and res[0] else []

    def get_my_registrations(self, client_id):
        query = SQLQueries.CLIENT_QUERIES["my_registrations"]
        res = self.db.execute_query(query, (client_id,), fetch=True)
        return res[0] if res and res[0] else []

    # --- ТВОЯ ИДЕАЛЬНАЯ БИЗНЕС-ЛОГИКА ---
    def register_for_class(self, client_id, schedule_id):
        profile_query = SQLQueries.CLIENT_QUERIES["profile"]
        profile_data = self.db.execute_query(profile_query, (client_id,), fetch=True)

        if not profile_data or not profile_data[0]:
            return False, "У вас нет оформленного абонемента."

        is_blocked = profile_data[0][0][4]
        client_access_level = profile_data[0][0][5]

        if is_blocked == 1:
            return False, "Ваш абонемент заблокирован. Запись невозможна."

        schedule_query = f"""
            SELECT z.capacity, z.required_access_level,
                   (SELECT COUNT(*) FROM class_registrations cr WHERE cr.schedule_id = sch.schedule_id AND cr.status = 'Записан') as registered_count
            FROM schedule sch
            JOIN zones z ON sch.zone_id = z.zone_id
            WHERE sch.schedule_id = %s;
        """
        sch_data = self.db.execute_query(schedule_query, (schedule_id,), fetch=True)
        if not sch_data or not sch_data[0]:
            return False, "Занятие не найдено."

        capacity, required_access, registered_count = sch_data[0][0]

        if registered_count >= capacity:
            return False, "К сожалению, свободных мест на это занятие больше нет."

        if client_access_level < required_access:
            return False, "Уровень вашего абонемента недостаточен для посещения этой зоны."

        # --- НОВАЯ ЛОГИКА: ПРОВЕРКА СУЩЕСТВУЮЩЕЙ ЗАПИСИ ---
        check_reg_query = "SELECT registration_id, status FROM class_registrations WHERE client_id = %s AND schedule_id = %s;"
        reg_data = self.db.execute_query(check_reg_query, (client_id, schedule_id), fetch=True)

        # Если клиент уже взаимодействовал с этой тренировкой
        if reg_data and reg_data[0]:
            reg_id, current_status = reg_data[0][0]

            if current_status == 'Записан':
                return False, "Вы уже записаны на эту тренировку."
            elif current_status == 'Отменено':
                # Восстанавливаем отмененную запись (меняем статус и обновляем время регистрации, чтобы она упала вниз списка)
                update_query = "UPDATE class_registrations SET status = 'Записан', registration_time = CURRENT_TIMESTAMP WHERE registration_id = %s;"
                success, _ = self.db.execute_query(update_query, (reg_id,), fetch=False)
                if success:
                    return True, "Вы успешно восстановили запись на тренировку!"
                return False, "Ошибка при восстановлении записи."
            else:
                return False, f"Невозможно записаться (текущий статус: {current_status})."

        # --- ЕСЛИ ЗАПИСИ НЕ БЫЛО: ОБЫЧНЫЙ INSERT ---
        insert_query = "INSERT INTO class_registrations (schedule_id, client_id, status) VALUES (%s, %s, 'Записан');"
        success, _ = self.db.execute_query(insert_query, (schedule_id, client_id), fetch=False)

        if success:
            return True, "Вы успешно записаны на тренировку!"
        return False, "Ошибка базы данных при записи."

    def cancel_registration(self, registration_id):
        time_query = SQLQueries.CLIENT_QUERIES["check_time_for_cancel"]
        time_data = self.db.execute_query(time_query, (registration_id,), fetch=True)

        if not time_data or not time_data[0]:
            return False, "Запись не найдена."

        hours_left = time_data[0][0][0]

        if hours_left is not None and hours_left < 2:
            return False, "Отмена невозможна: до начала тренировки осталось менее 2 часов."

        update_query = "UPDATE class_registrations SET status = 'Отменено' WHERE registration_id = %s;"
        success, _ = self.db.execute_query(update_query, (registration_id,), fetch=False)

        if success:
            return True, "Запись успешно отменена."
        return False, "Ошибка при отмене записи."