from typing import Any, Dict, List, Optional, Tuple

import psycopg2


class DBManager:
    """Класс для работы с БД PostgreSQL"""

    def __init__(self, config: Dict[str, str]):
        self.config = config

    def _connect(self):
        return psycopg2.connect(**self.config)

    def get_companies_and_vacancies_count(self) -> List[Tuple[Any]]:
        """Список всех компаний и количество вакансий у каждой"""
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, COUNT(v.vacancy_id) AS cnt
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.name
                ORDER BY cnt DESC, e.name;
            """
            )
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[Any]]:
        """Все вакансии: компания, название, зарплата, ссылка"""
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.title, v.salary_from, v.salary_to, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id;
            """
            )
            return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """Средняя зарплата по всем вакансиям"""
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG(
                    CASE
                        WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                            THEN (salary_from + salary_to) / 2.0
                        WHEN salary_to IS NOT NULL THEN salary_to::float
                        WHEN salary_from IS NOT NULL THEN salary_from::float
                        ELSE NULL
                    END
                )
                FROM vacancies;
            """
            )
            row = cur.fetchone()
            return row[0]  # float | None

    def get_vacancies_with_higher_salary(self) -> List[Tuple[Any]]:
        """Все вакансии, у которых зарплата выше средней по всем вакансиям"""
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                WITH avg_sal AS (
                    SELECT AVG(
                        CASE
                            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                                THEN (salary_from + salary_to) / 2.0
                            WHEN salary_to IS NOT NULL THEN salary_to::float
                            WHEN salary_from IS NOT NULL THEN salary_from::float
                            ELSE NULL
                        END
                    ) AS a
                    FROM vacancies
                )
                SELECT v.title, e.name,
                       CASE
                           WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                               THEN (v.salary_from + v.salary_to) / 2.0
                           WHEN v.salary_to IS NOT NULL THEN v.salary_to::float
                           WHEN v.salary_from IS NOT NULL THEN v.salary_from::float
                           ELSE NULL
                       END AS avg_salary,
                       v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id, avg_sal
                WHERE
                    CASE
                        WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                            THEN (v.salary_from + v.salary_to) / 2.0
                        WHEN v.salary_to IS NOT NULL THEN v.salary_to::float
                        WHEN v.salary_from IS NOT NULL THEN v.salary_from::float
                        ELSE NULL
                    END > avg_sal.a;
            """
            )
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[Any]]:
        """Вакансии, в названии которых содержится слово"""
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.title, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.title ILIKE %s;
            """,
                (f"%{keyword}%",),
            )
            return cur.fetchall()
