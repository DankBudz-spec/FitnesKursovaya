class SQLQueries:
    # Оставляем структуру TABLES как была, она нужна для генерации INSERT/UPDATE
    TABLES = {
        "membership_types": {"id": "type_id", "cols": ["title", "price", "duration_days", "access_level"],
                             "display_col": "title"},
        "clients": {"id": "client_id",
                    "cols": ["full_name", "phone_primary", "phone_secondary", "email", "birth_date", "address",
                             "registration_date", "medical_notes", "photo_path", "login", "password_hash"], "display_col": "full_name"},
        "staff": {"id": "staff_id",
                  "cols": ["full_name", "position", "specialization", "salary_rate", "phone", "hire_date", "login", "password_hash"],
                  "display_col": "full_name"},
        "classes": {"id": "class_type_id", "cols": ["name", "description"], "display_col": "name"},
        "zones": {"id": "zone_id", "cols": ["name", "capacity", "required_access_level"], "display_col": "name"},
        "equipment": {"id": "equipment_id", "cols": ["zone_id", "name", "purchase_date", "last_service_date", "status"],
                      "display_col": "name"},
        "client_subscriptions": {"id": "subscription_id",
                                 "cols": ["client_id", "type_id", "start_date", "end_date", "remaining_freeze_days",
                                          "is_blocked"]},
        "schedule": {"id": "schedule_id", "cols": ["class_type_id", "coach_id", "zone_id", "start_time", "end_time"]},
        "class_registrations": {"id": "registration_id",
                                "cols": ["schedule_id", "client_id", "registration_time", "status"]},
        "attendance_log": {"id": "visit_id", "cols": ["client_id", "entry_dt", "exit_dt"]},
        "payments": {"id": "payment_id", "cols": ["client_id", "amount", "payment_date", "payment_method"]}
    }

    # Специальные запросы с JOIN для отображения в главной таблице
    JOINED_QUERIES = {
        "equipment": "SELECT e.equipment_id, z.name, e.name, e.purchase_date, e.last_service_date, e.status FROM equipment e JOIN zones z ON e.zone_id = z.zone_id ORDER BY e.equipment_id",

        "client_subscriptions": "SELECT s.subscription_id, c.full_name, t.title, s.start_date, s.end_date, s.remaining_freeze_days, s.is_blocked FROM client_subscriptions s JOIN clients c ON s.client_id = c.client_id JOIN membership_types t ON s.type_id = t.type_id ORDER BY s.subscription_id",

        "schedule": "SELECT sch.schedule_id, cl.name, st.full_name, z.name, sch.start_time, sch.end_time FROM schedule sch JOIN classes cl ON sch.class_type_id = cl.class_type_id JOIN staff st ON sch.coach_id = st.staff_id JOIN zones z ON sch.zone_id = z.zone_id ORDER BY sch.schedule_id",

        "class_registrations": "SELECT r.registration_id, (cl.name || ' | ' || sch.start_time), c.full_name, r.registration_time, r.status FROM class_registrations r JOIN schedule sch ON r.schedule_id = sch.schedule_id JOIN classes cl ON sch.class_type_id = cl.class_type_id JOIN clients c ON r.client_id = c.client_id ORDER BY r.registration_id",

        "attendance_log": "SELECT a.visit_id, c.full_name, a.entry_dt, a.exit_dt FROM attendance_log a JOIN clients c ON a.client_id = c.client_id ORDER BY a.visit_id",

        "payments": "SELECT p.payment_id, c.full_name, p.amount, p.payment_date, p.payment_method FROM payments p JOIN clients c ON p.client_id = c.client_id ORDER BY p.payment_id"
    }

    # Добавь это в класс SQLQueries
    ANALYTICS_QUERIES = {
        # 1. Посещаемость по дням за последние 7 дней
        "visits_per_day": """
                SELECT DATE(entry_dt) as visit_date, COUNT(visit_id) as total_visits
                FROM attendance_log
                WHERE entry_dt >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY DATE(entry_dt)
                ORDER BY visit_date;
            """,

        # ИЗМЕНЕНО: Список должников (абонемент заблокирован ИЛИ срок действия истек)
        "debtors": """
                    SELECT c.full_name, c.phone_primary, s.start_date
                    FROM client_subscriptions s
                    JOIN clients c ON s.client_id = c.client_id
                    WHERE s.is_blocked = 1 OR s.end_date < CURRENT_DATE
                    ORDER BY s.start_date;
                """,

        # 3. Быстрые метрики (KPI): Общее количество активных клиентов
        "total_active_clients": """
                SELECT COUNT(DISTINCT client_id) 
                FROM client_subscriptions 
                WHERE is_blocked = 0 AND end_date >= CURRENT_DATE;
            """,

        # ИЗМЕНЕНО: АВТО-БЛОКИРОВКА: Ставит is_blocked = 1, если срок действия (end_date) истек
        "auto_block_debtors": """
                    UPDATE client_subscriptions
                    SET is_blocked = 1
                    WHERE is_blocked = 0 AND end_date < CURRENT_DATE;
                """,

        # 5. ПОСЕЩАЕМОСТЬ: Сводка за день, неделю, месяц (одним запросом)
        "attendance_summary": """
                SELECT 
                    (SELECT COUNT(*) FROM attendance_log WHERE DATE(entry_dt) = CURRENT_DATE) as today,
                    (SELECT COUNT(*) FROM attendance_log WHERE entry_dt >= CURRENT_DATE - INTERVAL '7 days') as week,
                    (SELECT COUNT(*) FROM attendance_log WHERE entry_dt >= CURRENT_DATE - INTERVAL '1 month') as month;
            """,

        # 6. ОБОРУДОВАНИЕ: Список инвентаря в ремонте
        "broken_equipment": """
                SELECT z.name as zone_name, e.name as equipment_name, e.last_service_date 
                FROM equipment e
                JOIN zones z ON e.zone_id = z.zone_id
                WHERE e.status = 'В ремонте';
            """,

        # --- НОВЫЕ ЗАПРОСЫ ДЛЯ ГРАФИКОВ ---
        "chart_day": """
                    SELECT EXTRACT(HOUR FROM entry_dt) AS hr, COUNT(visit_id)
                    FROM attendance_log
                    WHERE DATE(entry_dt) = CURRENT_DATE
                    GROUP BY hr ORDER BY hr;
                """,

        "chart_week": """
                    SELECT DATE(entry_dt), COUNT(visit_id)
                    FROM attendance_log
                    WHERE entry_dt >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY DATE(entry_dt) ORDER BY DATE(entry_dt);
                """,

        "chart_month": """
                    SELECT DATE(entry_dt), COUNT(visit_id)
                    FROM attendance_log
                    WHERE entry_dt >= CURRENT_DATE - INTERVAL '1 month'
                    GROUP BY DATE(entry_dt) ORDER BY DATE(entry_dt);
                """
    }

    # Запросы, фильтрующие данные ТОЛЬКО для конкретного тренера
    TRAINER_QUERIES = {
        # 1. Расписание только этого тренера
        "schedule": """
                SELECT sch.schedule_id, cl.name, st.full_name, z.name, sch.start_time, sch.end_time 
                FROM schedule sch 
                JOIN classes cl ON sch.class_type_id = cl.class_type_id 
                JOIN staff st ON sch.coach_id = st.staff_id 
                JOIN zones z ON sch.zone_id = z.zone_id 
                WHERE st.full_name = %s 
                ORDER BY sch.start_time;
            """,
        # 2. Записи клиентов только на занятия этого тренера
        "class_registrations": """
                SELECT r.registration_id, (cl.name || ' | ' || sch.start_time), c.full_name, r.registration_time, r.status 
                FROM class_registrations r 
                JOIN schedule sch ON r.schedule_id = sch.schedule_id 
                JOIN classes cl ON sch.class_type_id = cl.class_type_id 
                JOIN clients c ON r.client_id = c.client_id 
                JOIN staff st ON sch.coach_id = st.staff_id 
                WHERE st.full_name = %s 
                ORDER BY sch.start_time;
            """,
        # 3. Оборудование только в тех залах, где тренер проводит занятия
        "equipment": """
                SELECT e.equipment_id, z.name, e.name, e.purchase_date, e.last_service_date, e.status 
                FROM equipment e 
                JOIN zones z ON e.zone_id = z.zone_id 
                WHERE z.zone_id IN (
                    SELECT DISTINCT zone_id FROM schedule 
                    JOIN staff ON schedule.coach_id = staff.staff_id 
                    WHERE staff.full_name = %s
                )
                ORDER BY z.name, e.equipment_id;
            """
    }

    # Запросы для Личного кабинета клиента
    CLIENT_QUERIES = {
        # 1. Профиль: берем последний абонемент клиента, чтобы узнать статус и уровень доступа
        "profile": """
                SELECT t.title, s.start_date, s.end_date, s.remaining_freeze_days, s.is_blocked, t.access_level
                FROM client_subscriptions s
                JOIN membership_types t ON s.type_id = t.type_id
                WHERE s.client_id = %s
                ORDER BY s.end_date DESC LIMIT 1;
            """,

        # 2. Расписание: вычисляем свободные места (Вместимость зала МИНУС кол-во записанных)
        "available_schedule": """
                SELECT 
                    sch.schedule_id, 
                    cl.name as class_name, 
                    st.full_name as coach_name, 
                    z.name as zone_name, 
                    sch.start_time, 
                    sch.end_time,
                    (z.capacity - (
                        SELECT COUNT(*) 
                        FROM class_registrations cr 
                        WHERE cr.schedule_id = sch.schedule_id AND cr.status = 'Записан'
                    )) as available_spots,
                    z.required_access_level
                FROM schedule sch
                JOIN classes cl ON sch.class_type_id = cl.class_type_id
                JOIN staff st ON sch.coach_id = st.staff_id
                JOIN zones z ON sch.zone_id = z.zone_id
                WHERE DATE(sch.start_time) >= CURRENT_DATE
                ORDER BY sch.start_time;
            """,

        # 3. Мои записи: чтобы клиент видел, куда он записан, и мог отменить
        "my_registrations": """
                SELECT 
                    r.registration_id, 
                    cl.name as class_name, 
                    sch.start_time, 
                    r.status
                FROM class_registrations r
                JOIN schedule sch ON r.schedule_id = sch.schedule_id
                JOIN classes cl ON sch.class_type_id = cl.class_type_id
                WHERE r.client_id = %s
                ORDER BY r.registration_time ASC;
            """,

        # 4. Проверка времени до начала тренировки (для отмены)
        "check_time_for_cancel": """
                SELECT EXTRACT(EPOCH FROM (sch.start_time - CURRENT_TIMESTAMP)) / 3600 AS hours_left
                FROM class_registrations r
                JOIN schedule sch ON r.schedule_id = sch.schedule_id
                WHERE r.registration_id = %s;
            """
    }

    # Служебные запросы для контроллеров (Бизнес-логика)
    CONTROLLER_QUERIES = {
        "mark_attended": "UPDATE class_registrations SET status = 'Посетил' WHERE registration_id = %s;",
        "set_equipment_broken": "UPDATE equipment SET status = 'В ремонте' WHERE equipment_id = %s;",
        "get_freeze_info": "SELECT remaining_freeze_days, end_date FROM client_subscriptions WHERE subscription_id = %s;",
        "update_freeze": "UPDATE client_subscriptions SET end_date = %s, remaining_freeze_days = %s WHERE subscription_id = %s;",
        "check_overlap": "SELECT 1 FROM schedule WHERE coach_id = %s AND start_time < %s AND end_time > %s;",
        "check_overlap_exclude": "SELECT 1 FROM schedule WHERE coach_id = %s AND start_time < %s AND end_time > %s AND schedule_id != %s;"
    }

    @staticmethod
    def get_lookup_query(table_name):
        """Возвращает SQL запрос для выпадающих списков (ComboBox)"""
        if table_name == "clients":
            return "SELECT client_id, (full_name || ' | ' || phone_primary) FROM clients ORDER BY full_name;"
        elif table_name == "staff":
            return "SELECT staff_id, (full_name || ' | ' || position) FROM staff ORDER BY full_name;"
        elif table_name == "schedule":
            return """
                    SELECT sch.schedule_id, (cl.name || ' | ' || sch.start_time) 
                    FROM schedule sch 
                    JOIN classes cl ON sch.class_type_id = cl.class_type_id 
                    ORDER BY sch.start_time;
                """

        # Для остальных справочников генерируем автоматически
        info = SQLQueries.TABLES.get(table_name)
        if info:
            display_col = info.get("display_col", info["id"])
            return f"SELECT {info['id']}, {display_col} FROM {table_name} ORDER BY {display_col};"
        return None

    @staticmethod
    def get_select_all(table_name):
        # Если есть сложный JOIN-запрос, берем его, иначе просто SELECT *
        if table_name in SQLQueries.JOINED_QUERIES:
            return SQLQueries.JOINED_QUERIES[table_name] + ";"

        table_info = SQLQueries.TABLES.get(table_name)
        if table_info:
            return f"SELECT * FROM {table_name} ORDER BY {table_info['id']};"
        return None

    @staticmethod
    def get_insert_query(table_name, columns_count):
        table_info = SQLQueries.TABLES.get(table_name)
        cols_str = ", ".join(table_info["cols"])
        placeholders = ", ".join(["%s"] * columns_count)
        # Явное перечисление колонок защищает от ошибок синтаксиса
        return f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders});"

    @staticmethod
    def get_delete_query(table_name):
        table_info = SQLQueries.TABLES.get(table_name)
        return f"DELETE FROM {table_name} WHERE {table_info['id']} = %s;"

    @staticmethod
    def get_update_query(table_name):
        table_info = SQLQueries.TABLES.get(table_name)
        set_clause = ", ".join([f"{col}=%s" for col in table_info["cols"]])
        return f"UPDATE {table_name} SET {set_clause} WHERE {table_info['id']}=%s;"

    @staticmethod
    def get_auth_query(target):
        if target == "staff":
            # ДОБАВИЛИ staff_id
            return "SELECT staff_id, full_name, position, password_hash FROM staff WHERE login = %s;"
        if target == "clients":
            # ДОБАВИЛИ client_id
            return "SELECT client_id, full_name, 'Клиент' as position, password_hash FROM clients WHERE login = %s;"
        return None

    @staticmethod
    def get_select_by_id(table_name, columns="*"):
        """Универсальный запрос для вытаскивания любых полей по ID"""
        table_info = SQLQueries.TABLES.get(table_name)
        if not table_info:
            return None

        pk_col = table_info["id"]  # Программа сама знает, что у клиентов это client_id
        return f"SELECT {columns} FROM {table_name} WHERE {pk_col} = %s;"

