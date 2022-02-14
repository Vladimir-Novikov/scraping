import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
import json

vac_title = input("Укажите название должности: ").strip()
try:
    number_of_vacancies = int(input("Укажите кол-во вакансий (для вывода всех - ничего не указывайте): ")) + 1
except ValueError:
    number_of_vacancies = 10000

if number_of_vacancies < 0:  # преобразование в положительное число
    number_of_vacancies = (number_of_vacancies - 2) * -1

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
}

url = f"https://hh.ru/search/vacancy?search_field=name&search_field=company_nn&text={vac_title}&page=0&hhtmFrom=vacancy_search_list"
base_url = "https://hh.ru"

vacancy_list = []

print("Идет поиск...")
search = True
while search:
    # print(url)
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
                # если ограничение, указанное пользователем наступит раньше, чем пройдем по всем страницам, то json запишем в этом блоке
                if number_of_vacancies == len(vacancy_list) + 1:
                    print("Показано вакансий: ", len(vacancy_list))
                    search = False
                    with open(f"{vac_title}.json", "w", encoding="utf-8") as file:
                        json.dump(vacancy_list, file)
                    print(f"В файл {vac_title}.json внесено записей: {len(vacancy_list)}")
                    break
                else:
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
                        vacancy_div_tag_employer = vacancy.find(
                            "div", {"class": "vacancy-serp-item__meta-info-company"}
                        )
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

                    vacancy_list.append(vacancy_data)

            # ищем следующую страницу
            next_page = dom.find("a", {"data-qa": "pager-next"})
            if next_page:
                search_next_page = next_page["href"]
                url = base_url + search_next_page
            else:
                # если следующей страницы нет - пишем данные в json (если ограничение указанное пользователем наступит раньше, то запись произойдет в др блоке (см код выше))
                with open(f"{vac_title}.json", "w", encoding="utf-8") as file:
                    json.dump(vacancy_list, file)
                print(f"В файл {vac_title}.json внесено записей: {len(vacancy_list)}")
                break
        else:
            print(f"По запросу {vac_title} ничего не найдено")
            break
    else:
        print("Произошла ошибка, повторите запрос")
        break
