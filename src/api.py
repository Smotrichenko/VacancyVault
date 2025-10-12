from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API hh.ru"""

    def __init__(self, base_url: str, headers: Dict[str, str]) -> None:
        self._base_url = base_url
        self._headers = headers or {"User-Agent": "Vacancies-Client"}

    @abstractmethod
    def get_employers(self, ids: List[int]) -> List[Dict[str, Any]]:
        """Метод для получения данных о работодателях"""
        raise NotImplementedError

    @abstractmethod
    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """Метод для получения вакансий конкретного работодателя"""
        raise NotImplementedError


class HeadHunterAPI(VacancyAPI):
    """Класс работы с API hh.ru"""

    def __init__(self) -> None:
        super().__init__(base_url="https://api.hh.ru", headers=({"User-Agent": "HH-User-Agent"}))

    def get_employers(self, ids: List[int]) -> List[Dict[str, Any]]:
        data = []
        for emp_id in ids:
            try:
                resp = requests.get(f"{self._base_url}/employers/{emp_id}", headers=self._headers, timeout=10)
                if resp.status_code != 200:
                    print(f"employer {emp_id}: {resp.status_code}")
                    continue
                j = resp.json()
                data.append(j)
            except requests.RequestException:
                print(f"employer {emp_id}: network error")
                continue
        return data

    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        page = 0
        while page < 20:
            params = {"employer_id": employer_id, "per_page": 100, "page": page}
            try:
                resp = requests.get(f"{self._base_url}/vacancies", headers=self._headers, params=params, timeout=15)
                if resp.status_code != 200:
                    break
                j = resp.json()
                page_items = j.get("items", [])
                if not page_items:
                    break
                items.extend(page_items)

                total_pages = j.get("pages")
                page += 1
                if isinstance(total_pages, int) and page >= total_pages:
                    break
            except requests.RequestException:
                break
        return items
