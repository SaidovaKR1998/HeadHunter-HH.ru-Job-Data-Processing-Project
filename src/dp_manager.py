import psycopg2
from typing import List, Dict, Optional
from src.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


class DBManager:
    """Класс для управления базой данных вакансий"""

    def __init__(self, db_name):
        self.conn = psycopg2.connect(
            dbname=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

    def get_companies_and_vacancies_count(self):
        """Получает список всех компаний и количество вакансий у каждой компании"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name, COUNT(v.id) as vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.id = v.employer_id
                GROUP BY e.id, e.name
                ORDER BY vacancies_count DESC
            """)
            return cur.fetchall()

    def get_all_vacancies(self):
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name as company, v.title as vacancy, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                ORDER BY e.name, v.title
            """)
            return cur.fetchall()

    def get_avg_salary(self):
        """Получает среднюю зарплату по вакансиям"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
                FROM vacancies 
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            result = cur.fetchone()
            return result[0] if result else 0

    def get_vacancies_with_higher_salary(self):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name as company, v.title as vacancy, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > 
                      (SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                      FROM vacancies WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL)
                ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
            """)
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """Получает список всех вакансий, в названии которых содержатся переданные слова"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name as company, v.title as vacancy, 
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE v.title ILIKE %s OR v.description ILIKE %s
                ORDER BY e.name, v.title
            """, (f'%{keyword}%', f'%{keyword}%'))
            return cur.fetchall()

    def __del__(self):
        """Закрывает соединение при удалении объекта"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
