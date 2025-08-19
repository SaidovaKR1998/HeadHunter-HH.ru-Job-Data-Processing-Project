import psycopg2

def test_connection():
    """Функция для проверки подключения к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='Said43',  # Замените на ваш пароль
            host='localhost',
            port='5432'
        )
        print("✅ Успешное подключение к PostgreSQL!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    # Этот код выполнится только при прямом запуске файла
    test_connection()
