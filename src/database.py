import psycopg2
from psycopg2 import sql
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def create_database(self):
        """Создает базу данных"""
        try:
            # Подключаемся к postgres
            conn = psycopg2.connect(
                dbname='postgres',
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Завершаем соединения
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{self.db_name}'
                AND pid <> pg_backend_pid();
            """)

            # Удаляем и создаем базу
            cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
            cursor.execute(f"CREATE DATABASE {self.db_name} ENCODING 'UTF8'")

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            raise

    def create_tables(self):
        """Создает таблицы в базе данных"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                # Создание таблицы employers
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employers (
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        url VARCHAR(255),
                        description TEXT
                    )
                """)

                # Создание таблицы vacancies
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id INTEGER PRIMARY KEY,
                        employer_id INTEGER REFERENCES employers(id),
                        title VARCHAR(255) NOT NULL,
                        salary_from INTEGER,
                        salary_to INTEGER,
                        currency VARCHAR(10),
                        url VARCHAR(255),
                        description TEXT
                    )
                """)
            conn.commit()
            print("Таблицы успешно созданы")
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def connect(self):
        """Создает соединение с конкретной базой данных"""
        return psycopg2.connect(
            dbname=self.db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

    def save_data(self, employers, vacancies):
        """Сохраняет данные работодателей и вакансий в БД"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                # Сохраняем работодателей
                for employer in employers:
                    cursor.execute("""
                        INSERT INTO employers (id, name, url, description)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description
                    """, (
                        employer.get('id'),
                        employer.get('name', ''),
                        employer.get('url', ''),
                        employer.get('description', '')
                    ))

                # Сохраняем вакансии
                for vacancy in vacancies:
                    # Обрабатываем зарплату
                    salary = vacancy.get('salary', {})
                    salary_from = salary.get('from') if salary else None
                    salary_to = salary.get('to') if salary else None
                    currency = salary.get('currency') if salary else None

                    # Обрабатываем работодателя
                    employer_info = vacancy.get('employer', {}) or vacancy.get('employer', {})

                    cursor.execute("""
                        INSERT INTO vacancies (id, employer_id, title, salary_from, salary_to, currency, url, description)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                        employer_id = EXCLUDED.employer_id,
                        title = EXCLUDED.title,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description
                    """, (
                        vacancy.get('id'),
                        employer_info.get('id'),
                        vacancy.get('name', ''),
                        salary_from,
                        salary_to,
                        currency,
                        vacancy.get('alternate_url', ''),
                        vacancy.get('description', '')  # Используем get с default значением
                    ))

            conn.commit()
            print("Данные успешно сохранены в БД")

        except psycopg2.Error as e:
            print(f"Ошибка при сохранении данных: {e}")
            conn.rollback()
            raise
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            print(f"Проблемная вакансия: {vacancy}")
            conn.rollback()
            raise
        finally:
            conn.close()
