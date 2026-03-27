import html
import re
from typing import Any, Dict


def normalize_employer(j: Dict[str, Any]) -> Dict[str, Any]:
    """Нормализация работодателей"""

    desc_raw = j.get("description") or ""
    desc_clean = html.unescape(re.sub(r"<[^>]+>", "", desc_raw)).strip()

    return {
        "employer_id": int(j["id"]),
        "name": j.get("name") or "Без названия",
        "url": j.get("alternate_url"),
        "open_vacancies": int(j.get("open_vacancies") or 0),
        "description": desc_clean,
    }


def normalize_vacancy(j: Dict[str, Any]) -> Dict[str, Any]:
    """Нормализация вакансий работодателей"""

    sal = j.get("salary") or {}
    return {
        "vacancy_id": int(j["id"]),
        "employer_id": int((j.get("employer") or {}).get("id")),
        "title": j.get("name") or "Без названия",
        "url": j.get("alternate_url"),
        "salary_from": sal.get("from"),
        "salary_to": sal.get("to"),
        "currency": sal.get("currency"),
        "requirement": (j.get("snippet") or {}).get("requirement"),
        "responsibility": (j.get("snippet") or {}).get("responsibility"),
    }
