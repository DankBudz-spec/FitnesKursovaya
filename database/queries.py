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
            return "SELECT full_name, position, password_hash FROM staff WHERE login = %s;"
        if target == "clients":
            return "SELECT full_name, 'Клиент' as position, password_hash FROM clients WHERE login = %s;"
        return None

    @staticmethod
    def get_select_by_id(table_name, columns="*"):
        """Универсальный запрос для вытаскивания любых полей по ID"""
        table_info = SQLQueries.TABLES.get(table_name)
        if not table_info:
            return None

        pk_col = table_info["id"]  # Программа сама знает, что у клиентов это client_id
        return f"SELECT {columns} FROM {table_name} WHERE {pk_col} = %s;"

