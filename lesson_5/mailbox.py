from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date, timedelta
from secrets import secret_login, secret_password
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import hashlib

# блок работы с Mongo
client = MongoClient("127.0.0.1", 27017)
db = client["mail_ru"]  # создали БД
mailbox = db.mailbox  # создали коллекцию


month_list = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]

# текущая дата для исправления формата даты в письмах с Сегодня -> 12 мая
today = date.today()
yesterday = today - timedelta(days=1)
today_date = f"{today.day} {month_list[today.month - 1]}"
yesterday_date = f"{yesterday.day} {month_list[yesterday.month - 1]}"

s = Service("./chromedriver")
chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(service=s, options=chrome_options)
driver.implicitly_wait(10)

driver.get("https://account.mail.ru/login")

# заполнение регистрационных данных
username = driver.find_element(By.XPATH, "//input[@name='username']")
username.send_keys(secret_login)
username.send_keys(Keys.ENTER)

password = driver.find_element(By.XPATH, "//input[@name='password']")
password.send_keys(secret_password)
password.send_keys(Keys.ENTER)

href_set = set()

last_letter = ""

while True:
    letters = driver.find_elements(
        By.XPATH,
        "//a[contains(@class, 'llc_new llc_new-selection js-letter-list-item')]",
    )
    for el in letters:
        href = el.get_attribute("href")
        href_set.add(href)
    next_letter = letters[-1]
    if next_letter == last_letter:
        break

    # находим последний элемент и переходим к нему
    actions = ActionChains(driver)
    actions.move_to_element(next_letter)
    actions.perform()
    last_letter = next_letter

print(f"Найдено писем: {len(href_set)}")


for href_item in href_set:
    letter_data = {}
    driver.get(href_item)

    author_info = driver.find_element(By.XPATH, "//div[@class ='letter__author']")
    contact = author_info.find_element(By.XPATH, "./span[@class ='letter-contact']")
    contact_name = contact.get_attribute("textContent")
    contact_email = contact.get_attribute("title")
    time_date = author_info.find_element(By.XPATH, "./div[@class='letter__date']").get_attribute("textContent")
    if "Вчера" in time_date:
        time_date = time_date.replace("Вчера", yesterday_date)
    elif "Сегодня" in time_date:
        time_date = time_date.replace("Сегодня", today_date)
    else:
        pass

    title = driver.find_element(By.XPATH, "//h2[@class='thread-subject']").get_attribute("textContent")
    text = driver.find_element(By.XPATH, "//div[@class ='letter-body']").get_attribute("textContent")

    pre_text = text.replace("\n", "").split(" ")
    text_list = []
    for i in pre_text:
        if i != "" and i != " ":
            text_list.append(i)
    new_text = " ".join(text_list)

    hash_data = contact_email + title
    letter_data["_id"] = hashlib.md5(hash_data.encode()).hexdigest()
    letter_data["from"] = contact_name
    letter_data["from_email"] = contact_email
    letter_data["date"] = time_date
    letter_data["title"] = title
    letter_data["text"] = new_text

    try:
        mailbox.insert_one(letter_data)
    except DuplicateKeyError:
        print("Запись уже существует в БД")

driver.close()
print(f"Всего записей в коллекции mailbox: {len(list(db.mailbox.find()))}")
