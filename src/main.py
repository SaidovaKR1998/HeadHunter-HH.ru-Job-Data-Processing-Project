from src.hh_api import HeadHunterAPI
from src.database import Database
from src.dp_manager import DBManager
from src.config import DB_NAME, EMPLOYER_IDS


def main():
    # Создаем базу данных и таблицы
    db = Database(DB_NAME)
    db.create_database()
    db.create_tables()

    # Получаем данные с hh.ru
    hh_api = HeadHunterAPI()
    employers = hh_api.get_employers(EMPLOYER_IDS)
    vacancies = []
    for employer_id in EMPLOYER_IDS:
        vacancies.extend(hh_api.get_vacancies(employer_id))

    # Сохраняем данные в БД
    db.save_data(employers, vacancies)

    # Работа с данными через DBManager
    db_manager = DBManager(DB_NAME)

    while True:
        print("\nВыберите действие:")
        print("1. Список компаний и количество вакансий")
        print("2. Список всех вакансий")
        print("3. Средняя зарплата по вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("> ")

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company[0]}: {company[1]} вакансий")

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            for vacancy in vacancies:
                salary = f"{vacancy[2]}-{vacancy[3]} {vacancy[4]}"
                print(f"{vacancy[0]}: {vacancy[1]}, Зарплата: {salary}")
                print(f"Ссылка: {vacancy[5]}\n")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"Средняя зарплата по вакансиям: {avg_salary:.2f}")

        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            for vacancy in vacancies:
                salary = f"{vacancy[2]}-{vacancy[3]} {vacancy[4]}"
                print(f"{vacancy[0]}: {vacancy[1]}, Зарплата: {salary}")
                print(f"Ссылка: {vacancy[5]}\n")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            for vacancy in vacancies:
                salary = f"{vacancy[2]}-{vacancy[3]} {vacancy[4]}"
                print(f"{vacancy[0]}: {vacancy[1]}, Зарплата: {salary}")
                print(f"Ссылка: {vacancy[5]}\n")

        elif choice == "0":
            break

        else:
            print("Неверный ввод")


if __name__ == "__main__":
    main()
