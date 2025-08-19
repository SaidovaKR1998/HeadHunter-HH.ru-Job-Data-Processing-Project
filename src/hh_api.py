import requests
from typing import Dict, List, Optional


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = "https://api.hh.ru"

    def get_employers(self, employer_ids: List[int]) -> List[Dict]:
        """Получение данных о работодателях по их ID"""
        employers = []
        for employer_id in employer_ids:
            url = f"{self.base_url}/employers/{employer_id}"
            response = requests.get(url)
            if response.status_code == 200:
                employer_data = response.json()
                employers.append({
                    'id': employer_data['id'],
                    'name': employer_data['name'],
                    'url': employer_data['site_url'],
                    'description': employer_data.get('description', '')
                })
        return employers

    def get_vacancies(self, employer_id: int) -> List[Dict]:
        """Получение вакансий работодателя по его ID"""
        url = f"{self.base_url}/vacancies?employer_id={employer_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('items', [])
        return []
