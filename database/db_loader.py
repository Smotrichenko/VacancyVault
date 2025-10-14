from typing import Dict, List

import psycopg2

from utils.config import load_config


def insert_employers(employers: List[Dict]) -> None:
    """Вставка нормализованных данных в таблицу"""

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                            INSERT INTO employers (employer_id, name, url, open_vacancies, description)
                            VALUES (%(employer_id)s, %(name)s, %(url)s, %(open_vacancies)s, %(description)s)
                            ON CONFLICT (employer_id) DO UPDATE
                            SET name = EXCLUDED.name,
                                url = EXCLUDED.url,
                                open_vacancies = EXCLUDED.open_vacancies,
                                description = EXCLUDED.description;
                        """,
                employers,
            )


def insert_vacancy(vacancies: List[Dict]) -> None:
    """Вставка нормализованных данных в таблицу"""

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                    INSERT INTO vacancies (vacancy_id, employer_id, title, url,
                                           salary_from, salary_to, currency, requirement, responsibility)
                    VALUES (%(vacancy_id)s, %(employer_id)s, %(title)s, %(url)s,
                            %(salary_from)s, %(salary_to)s, %(currency)s, %(requirement)s, %(responsibility)s)
                    ON CONFLICT (vacancy_id) DO NOTHING;
                """,
                vacancies,
            )
