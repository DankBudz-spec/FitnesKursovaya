import psycopg2


def check_db_connection():
    connection_params = {
        "host": "localhost",
        "port": 5432,
        "database": "fitness_db",
        "user": "postgres",
        "password": "mysecretpassword",
    }

    connection = None
    cursor = None

    try:
        print("🔌 Попытка подключения к базе данных...")

        connection = psycopg2.connect(**connection_params)

        cursor = connection.cursor()

        print("🎉 Успешно подключено к PostgreSQL!")

        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()

        print(f"📟 Версия вашей СУБД: {db_version[0]}")

    except Exception as error:
        print("❌ Ошибка при подключении к базе данных!")
        print(f"Детали ошибки: {error}")

    finally:
        if cursor:
            cursor.close()
            print("🚪 Курсор закрыт.")
        if connection:
            connection.close()
            print("🔌 Соединение с БД закрыто.")


if __name__ == "__main__":
    check_db_connection()