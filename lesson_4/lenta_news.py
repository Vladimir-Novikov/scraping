from pprint import pprint
import requests
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import re


url = "https://lenta.ru/"
base_url = "https://lenta.ru"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
}

# блок работы с Mongo
client = MongoClient("127.0.0.1", 27017)
db = client["news_db"]  # создали БД
lenta_news = db.lenta_news  # создали коллекцию


response = requests.get(url, headers=headers)
if response.ok:
    print("Собираем новости ... ")
    dom = html.fromstring(response.text)

    links_list = dom.xpath("//a[contains(@class, 'card-')]")
    for link in links_list:
        news_data = {}
        # на сайте есть ссылки с полным и не полным путем. Проверяем и дополняем в случае необходимости
        link_path = link.xpath(".//@href")[0]
        if link_path[0] == "/":
            url = base_url + link_path
        else:
            url = link_path

        # дата в зависимости от ссылки есть двух видов
        date_time = re.findall("\d{4}\/\d{2}\/\d{2}", url)

        if not date_time:
            date_time = re.findall("\d{2}\-\d{2}\-\d{4}", url)

        # заголовки в зависимости от важности есть двух видов
        news_title = link.xpath(".//h3[contains(@class,'__title')]/text()")
        if not news_title:
            news_title = link.xpath(".//span[contains(@class,'__title')]//text()")

        news_data["_id"] = url  # ссылка на новость является и ID записи
        news_data["url"] = url
        news_data["source"] = base_url
        news_data["date"] = date_time[0]
        news_data["title"] = news_title[0]
        try:
            lenta_news.insert_one(news_data)
        except DuplicateKeyError:
            print("Запись уже существует в БД")

else:
    print("Ошибка запроса")

print(f"Всего записей в коллекции lenta_news: {len(list(db.lenta_news.find()))}")
