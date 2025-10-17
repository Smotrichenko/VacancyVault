from database.db_creator import create_tables
from database.db_loader import insert_employers, insert_vacancy
from database.db_manager import DBManager
from src.api import HeadHunterAPI
from utils.config import load_config
from utils.normalize import normalize_employer, normalize_vacancy


def show_menu() -> None:
    print(
        "\n===== VacancyVault =====\n"
        "1 — Компании и количество вакансий\n"
        "2 — Все вакансии (компания/вакансия/зп/ссылка)\n"
        "3 — Средняя зарплата по вакансиям\n"
        "4 — Вакансии с зарплатой выше средней\n"
        "5 — Поиск вакансий по слову\n"
        "0 — Выход\n"
    )


def main() -> None:
    """Основная функция"""

    create_tables()

    hh = HeadHunterAPI()
    EMPLOYER_IDS = [1740, 3529, 78638, 1373, 949811, 4219, 3776, 1122462, 4454792, 3627]

    # Получаем данные
    employers_raw = hh.get_employers(EMPLOYER_IDS)
    employers = [normalize_employer(e) for e in employers_raw]
    insert_employers(employers)

    all_vacancies_raw = []
    for eid in EMPLOYER_IDS:
        all_vacancies_raw.extend(hh.get_vacancies(eid))
    vacancies = [normalize_vacancy(v) for v in all_vacancies_raw]
    insert_vacancy(vacancies)

    print(f"Загружено: работодателей={len(employers)}; вакансий={len(vacancies)}")

    db = DBManager(load_config())
    # Интерфейс взаимодествия с пользователем
    while True:
        show_menu()
        choice = input("Выберите пункт: ").strip()

        if choice == "1":
            rows = db.get_companies_and_vacancies_count()
            if not rows:
                print("Нет данных.")
            else:
                for name, cnt in rows:
                    print(f"- {name}: {cnt}")

        elif choice == "2":
            rows = db.get_all_vacancies()
            if not rows:
                print("Нет вакансий.")
            else:
                for company, title, s_from, s_to, url in rows[:25]:
                    salary = (
                        f"{s_from}-{s_to}"
                        if (s_from and s_to)
                        else (str(s_from) if s_from else (str(s_to) if s_to else "не указана"))
                    )
                    print(f"- {company} — {title} — з/п: {salary} — {url}")

        elif choice == "3":
            avg = db.get_avg_salary()
            print(f"Средняя зарплата: {round(avg) if avg else 'нет данных'}")

        elif choice == "4":
            rows = db.get_vacancies_with_higher_salary()
            if not rows:
                print("Нет вакансий выше средней.")
            else:
                for title, company, avg_salary, url in rows[:100]:
                    print(f"- {company} — {title} — ~{int(avg_salary)} — {url}")

        elif choice == "5":
            kw = input("Ключевое слово (например, python): ").strip()
            if not kw:
                print("Пустой запрос.")
                continue
            rows = db.get_vacancies_with_keyword(kw)
            if not rows:
                print("Ничего не найдено.")
            else:
                for company, title, url in rows[:100]:
                    print(f"- {company} — {title} — {url}")

        elif choice == "0":
            print("Пока!")
            break

        else:
            print("Неизвестная команда. Повторите ввод.")


if __name__ == "__main__":
    main()
