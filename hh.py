from bs4 import *
import requests
import json
import time
import re

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'accept': '*/*'}


# search validation by length
def validation(search: str) -> None:
    if len(search) <= 3:
        raise Exception('Search is too short')
    elif len(search) >= 60:
        raise Exception('Search is too long')


def get_vacancies_list(search: str) -> None:
    """
    :param search: type vacancy that you want to find
    :return: creating or updating, sorted json file with skills from all vacancies from search
    """
    validation(search)
    r = requests.get(f'https://api.hh.ru/vacancies/', params={'text': f'{search}', 'per_page': '0'}, headers=HEADERS)
    print(r.status_code)
    number_of_vacancies = r.json()['found']
    page = 0
    id_of_vacancies = []
    # Получаем все id у вакансий
    for iteration in range(number_of_vacancies // 100 + 1):
        vacancies = requests.get(f'https://api.hh.ru/vacancies/',
                                 params={'text': f'{search}', 'per_page': '100', 'page': f'{page}'}, headers=HEADERS)
        try:
            for item in vacancies.json()['items']:
                id_of_vacancies.append(item['id'])
            page += 1
        except KeyError:
            page += 1

    # Получаем все скиллы требуемые для вакансии и загружаем их куда нибудь
    skills = {}
    for id in id_of_vacancies:
        vacancy = requests.get(f'https://api.hh.ru/vacancies/{id}', headers=HEADERS)
        try:
            vacancy.json()['key_skills']
        except KeyError:
            continue
        else:
            for skill in vacancy.json()['key_skills']:
                if skill['name'] not in skills.keys():
                    skills.setdefault(skill['name'], 1)
                else:
                    skills[skill['name']] += 1

    # сортировка и выгрузка в data.json файл
    skills['total_amount_of_vacancies'] = len(id_of_vacancies)
    sorted_keys = sorted(skills, key=skills.get, reverse=True)
    sorted_skills = {}
    for w in sorted_keys:
        sorted_skills[w] = skills[w]

    with open(f'data_{search}.json', 'w+') as file:
        json.dump(sorted_skills, file, ensure_ascii=False, indent=4)


get_vacancies_list('django junior')
