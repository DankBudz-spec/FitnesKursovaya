class SQLQueries:
    TABLES = {
        "membership_types": {
            "id": "type_id",
            "cols": ["title", "price", "duration_days", "access_level"]
        },
        "clients": {
            "id": "client_id",
            "cols": ["full_name", "phone_primary", "phone_secondary", "email", "birth_date", "address",
                     "registration_date", "medical_notes", "photo_path"]
        },
        "staff": {
            "id": "staff_id",
            "cols": ["full_name", "position", "specialization", "salary_rate", "phone", "hire_date"]
        },
        "classes": {
            "id": "class_type_id",
            "cols": ["name", "description"]
        },
        "zones": {
            "id": "zone_id",
            "cols": ["name", "capacity", "required_access_level"]
        },
        "equipment": {
            "id": "equipment_id",
            "cols": ["zone_id", "name", "purchase_date", "last_service_date", "status"]
        },
        "client_subscriptions": {
            "id": "subscription_id",
            "cols": ["client_id", "type_id", "start_date", "end_date", "remaining_freeze_days", "is_blocked"]
        },
        "schedule": {
            "id": "schedule_id",
            "cols": ["class_type_id", "coach_id", "zone_id", "start_time", "end_time"]
        },
        "class_registrations": {
            "id": "registration_id",
            "cols": ["schedule_id", "client_id", "registration_time", "status"]
        },
        "attendance_log": {
            "id": "visit_id",
            "cols": ["client_id", "entry_dt", "exit_dt"]
        },
        "payments": {
            "id": "payment_id",
            "cols": ["client_id", "amount", "payment_date", "payment_method"]
        }
    }

    @staticmethod
    def get_select_all(table_name):
        table_info = SQLQueries.TABLES.get(table_name)
        if table_info:
            return f"SELECT * FROM {table_name} ORDER BY {table_info['id']};"
        return None

    @staticmethod
    def get_insert_query(table_name, columns_count):
        placeholders = ", ".join(["%s"] * columns_count)
        return f"INSERT INTO {table_name} VALUES (DEFAULT, {placeholders});"

    @staticmethod
    def get_delete_query(table_name):
        table_info = SQLQueries.TABLES.get(table_name)
        if table_info:
            return f"DELETE FROM {table_name} WHERE {table_info['id']} = %s;"
        return None

    @staticmethod
    def get_update_query(table_name):
        table_info = SQLQueries.TABLES.get(table_name)
        if not table_info:
            return None

        set_clause = ", ".join([f"{col}=%s" for col in table_info["cols"]])
        return f"UPDATE {table_name} SET {set_clause} WHERE {table_info['id']}=%s;"