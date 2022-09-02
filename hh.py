
import ujson
import time
import re
import asyncio
from datetime import datetime
from aiohttp import ClientSession
import requests


try:
    app_token = open('app_token.txt', 'r').readline()
except FileNotFoundError:
    app_token = None

if app_token:
    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'accept': '*/*',
        'Authorization': 'Bearer ' + app_token
        }

else:
    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'accept': '*/*',
        }


# search validation by length
def validation(search: str) -> None:
    if len(search) <= 3:
        raise Exception('Search is too short')
    elif len(search) >= 60:
        raise Exception('Search is too long')


async def get_vacancies_list(search: str) -> None:
    """
    :param search: type vacancy that you want to find
    :return: creating or updating, sorted json file with skills from all vacancies from search
    """
    validation(search)
    r = requests.get(f'https://api.hh.ru/vacancies/', params={'text': f'{search}', 'per_page': '0'}, headers=HEADERS)
    number_of_vacancies = r.json()['found']
    page = 0
    id_of_vacancies = []

    # Получаем все id у вакансий
    async with ClientSession() as session:
        for iteration in range(number_of_vacancies // 100 + 1):
            async with session.get(f'https://api.hh.ru/vacancies/',
                                     params={'text': f'{search}', 'per_page': '100', 'page': f'{page}'}, headers=HEADERS) as vacancies:
                try:
                    vacancies_json = await vacancies.json()
                    for item in vacancies_json['items']:
                        id_of_vacancies.append(item['id'])
                    page += 1
                except KeyError:
                    page += 1

    # Получаем все скиллы требуемые для вакансии и загружаем их куда нибудь
    skills = {}
    async with ClientSession() as session:
        for id in id_of_vacancies:
            async with session.get(f'https://api.hh.ru/vacancies/{id}', headers=HEADERS) as vacancy:
                try:

                    vacancy = await vacancy.json()
                    vacancy['key_skills']
                except KeyError:

                    continue
                else:
                    for skill in vacancy['key_skills']:
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
        ujson.dump(sorted_skills, file, ensure_ascii=False, indent=4)


asyncio.run(get_vacancies_list(str(input('Введите название вакансий которые вы хотите посмотреть: '))))
