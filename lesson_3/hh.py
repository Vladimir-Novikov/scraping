import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
import hashlib
from pymongo import MongoClient

vac_title = input("Укажите название должности: ").strip()
try:
    number_of_vacancies = int(input("Укажите кол-во вакансий для поиска (для вывода всех - ничего не указывайте): "))
except ValueError:
    number_of_vacancies = 10000

if number_of_vacancies < 0:  # преобразование в положительное число
    number_of_vacancies *= -1

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
}

url = f"https://hh.ru/search/vacancy?search_field=name&search_field=company_nn&text={vac_title}&page=0&hhtmFrom=vacancy_search_list"
base_url = "https://hh.ru"

records = 0  # кол-во новых записей
duplicate = 0  # кол-во найденых дубликатов

# блок работы с Mongo
client = MongoClient("127.0.0.1", 27017)
db = client["hh_ru_vacancies"]  # создали БД
vacancies = db.vacancies  # создали коллекцию


def fill_db(data):
    # проверка на уникальность ID происходит в ф-ции find_id, поэтому здесь обходимся без try except
    vacancies.insert_one(data)


def id_hash(data):
    # функция получает сконкотенорованную строку и возвращает хэш для ID
    hash_object = hashlib.md5(data.encode())
    return hash_object.hexdigest()


def find_id(hash_id):
    return bool(vacancies.find_one({"_id": hash_id}))


print("Идет поиск...")
search = True
while records < number_of_vacancies:
    try:
        response = requests.get(url, headers=headers)
    except Exception as err:
        print("Ошибка запроса: ", err)
        break
    if response.ok:
        dom = BeautifulSoup(response.text, "html.parser")
        all_vacancies = dom.find_all("div", {"class": "vacancy-serp-item"})
        if all_vacancies:
            for vacancy in all_vacancies:
                vacancy_data = {}
                # тег содержащий название и ссылку на вакансию
                vacancy_a_tag_title = vacancy.find("a", {"data-qa": "vacancy-serp__vacancy-title"})
                vacancy_title = vacancy_a_tag_title.get_text()
                vacancy_href = vacancy_a_tag_title["href"]

                # тег содержащий название и ссылку на работодателя
                vacancy_a_tag_employer = vacancy.find("a", {"data-qa": "vacancy-serp__vacancy-employer"})
                if vacancy_a_tag_employer:
                    vacancy_employer = vacancy_a_tag_employer.get_text().replace("\xa0", " ")
                    vacancy_employer_href = base_url + vacancy_a_tag_employer["href"]
                else:  # если работодатель не указан - берем другой тег
                    vacancy_div_tag_employer = vacancy.find("div", {"class": "vacancy-serp-item__meta-info-company"})
                    vacancy_employer = vacancy_div_tag_employer.get_text().replace("\xa0", " ")
                    vacancy_employer_href = None

                # тег с информацией о зарплате
                salary = vacancy.find("span", {"data-qa": "vacancy-serp__vacancy-compensation"})

                salary_dict = {}
                if salary:
                    upper_str = salary.get_text().upper()

                    rep = ["\u202f", ".", "\xa0"]
                    for item in rep:
                        if item in upper_str:
                            upper_str = upper_str.replace(item, "")

                    currency = re.findall("[А-ЯЁA-Z]{3}", salary.get_text().upper())  # валюта
                    if len(currency) > 1:
                        currency = currency[0] + currency[1]
                        # удалем обозначение валюты из строки (для двойных названий БЕЛ РУБ например)
                        upper_str = upper_str.replace(currency, " ")
                        currency = [currency]
                    else:
                        upper_str = upper_str.replace(
                            currency[0], " "
                        )  # удалем обозначение валюты из строки (для стандартных трех символов)

                    split_string = upper_str.split("–")  # разделяем строку для нахождения мин и макс

                    if len(split_string) == 2:
                        min_salary = int(split_string[0].strip())
                        max_salary = int(split_string[1].strip())
                    else:
                        range_search = upper_str.strip().split(" ")
                        if range_search[0] == "ОТ":
                            min_salary = int(range_search[1])
                            max_salary = None
                        elif range_search[0] == "ДО":
                            min_salary = None
                            max_salary = int(range_search[1])
                        else:
                            min_salary = None
                            max_salary = None

                # если информации о зарплате нет - пишем None
                else:
                    min_salary = None
                    max_salary = None
                    currency = None

                # блок записи данных из текущей итерации в словарь
                # данные о зарплате
                salary_dict["min_salary"] = min_salary
                salary_dict["max_salary"] = max_salary
                if currency:
                    currency = currency[0]  # распаковка листа
                salary_dict["currency"] = currency

                # данные о вакансии, работодателе, ресурсе (hh.ru) и зарплате
                vacancy_data["vacancy_title"] = vacancy_title
                vacancy_data["salary_data"] = salary_dict
                vacancy_data["vacancy_href"] = vacancy_href
                vacancy_data["source"] = base_url
                vacancy_data["employer"] = vacancy_employer
                vacancy_data["employer_href"] = vacancy_employer_href

                # конкатенация нескольких полей для получения уникального хэш
                data_id_hash = vacancy_title + vacancy_employer + str(min_salary) + str(max_salary)

                hash_id = id_hash(data_id_hash)  # получили хэш

                if not find_id(hash_id):  # передали полученный хэш - ID для документа в функцию
                    # если такого ID в коллекции нет ни у одного документа - присваеваем этот ID текущему документу
                    vacancy_data["_id"] = hash_id
                    fill_db(vacancy_data)  # вносим документ в коллекцию (БД)
                    records += 1
                else:
                    duplicate += 1

                if records == number_of_vacancies:
                    break
            # ищем следующую страницу
            next_page = dom.find("a", {"data-qa": "pager-next"})
            if next_page:
                search_next_page = next_page["href"]
                url = base_url + search_next_page
            else:
                # если следующей страницы нет - выходим из цикла
                break
        else:
            print(f"По запросу {vac_title} ничего не найдено")
            break
    else:
        print("Произошла ошибка, повторите запрос")
        break


print(f"Внесено новых/уникальных записей: {records}")
print(f"Всего записей в коллекции vacancies: {len(list(db.vacancies.find()))}")
print(f"При скрапинге встретилось дублирующих записей: {duplicate}")

while True:
    try:
        desired_salary = int(input("Укажите желаемую зарплату (целое число): "))
    except ValueError:
        continue

    if desired_salary < 0:  # преобразование в положительное число
        desired_salary *= -1
    break

while True:
    currency_name = (
        input("Укажите валюту (например руб, usd, kzt, бел). Оставьте ПУСТОЕ ПОЛЕ для всех вариантов: ")
        .replace(" ", "")
        .upper()[:3]
    )
    if not currency_name:
        currency_name = ""
    break

print(f"Ищем вакансии с зарплатой выше {desired_salary} {currency_name}...")
# поиск по БД идет по валюте и двум полям зарплаты
for item in vacancies.find(
    {
        "salary_data.currency": {"$regex": currency_name},
        "$or": [
            {"salary_data.min_salary": {"$gte": desired_salary}},
            {"salary_data.max_salary": {"$gte": desired_salary}},
        ],
    }
):

    pprint(item)
