from pprint import pprint
import requests
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

url = "https://news.mail.ru/"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
}

# блок работы с Mongo
client = MongoClient("127.0.0.1", 27017)
db = client["news_db"]  # создали БД
mail_news = db.mail_news  # создали коллекцию


response = requests.get(url, headers=headers)
if response.ok:
    print("Собираем новости ... ")
    dom = html.fromstring(response.text)

    links_list = []

    main_news = dom.xpath("//div[contains(@class,'daynews__item')]//@href")
    links_list.extend(main_news)
    sub_main_news = dom.xpath("//div[@class='js-module']//li[@class='list__item']//@href")
    links_list.extend(sub_main_news)

    news_blocks = dom.xpath("//div[@class='cols__inner']//a[contains(@class, 'link')]/@href")
    links_list.extend(news_blocks)

    for url in links_list:
        news_data = {}

        response = requests.get(url, headers=headers)
        if response.ok:
            dom = html.fromstring(response.text)

            news_title = dom.xpath("//h1[@class='hdr__inner']//text()")[0]
            info_block = dom.xpath("//div[contains(@class,'breadcrumbs')]")
            for item in info_block:
                date_time = item.xpath(".//@datetime")[0]
                source = item.xpath(".//span[@class='link__text']//text()")[0]
            news_data["_id"] = url  # ссылка на новость является и ID записи
            news_data["url"] = url
            news_data["source"] = source
            news_data["date"] = date_time
            news_data["title"] = news_title
            try:
                mail_news.insert_one(news_data)
            except DuplicateKeyError:
                print("Запись уже существует в БД")
        else:
            continue
else:
    print("Ошибка запроса")

print(f"Всего записей в коллекции mail_news: {len(list(db.mail_news.find()))}")
