import psycopg2

from utils.config import load_config


def create_tables():
    """Функция создания таблиц для Базы Данных"""

    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                employer_id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url TEXT,
                open_vacancies INTEGER,
                description TEXT
                );
            """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id INTEGER PRIMARY KEY,
                employer_id INTEGER REFERENCES employers (employer_id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                url TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                requirement TEXT,
                responsibility TEXT,
                CHECK (salary_from IS NULL OR salary_from >= 0),
                CHECK (salary_to   IS NULL OR salary_to   >= 0),
                CHECK (salary_from IS NULL OR salary_to IS NULL OR salary_to >= salary_from)
            );
        """
            )
