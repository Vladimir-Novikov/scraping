from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


# блок работы с Mongo
client = MongoClient("127.0.0.1", 27017)
db = client["mvideo"]  # создали БД
trend = db.trend  # создали коллекцию

s = Service("./chromedriver")
chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(service=s, options=chrome_options)
driver.implicitly_wait(10)

driver.get("https://www.mvideo.ru/")


for i in range(5):
    try:
        button = driver.find_element(By.XPATH, "//span[contains(text(),'В тренде')]")
        number = button.find_element(By.XPATH, "./parent::div/span[@class='count']").get_attribute("textContent")
        button.click()
        break
    except NoSuchElementException:
        html = driver.find_element(By.TAG_NAME, "html")
        html.send_keys(Keys.PAGE_DOWN)
        continue


products = driver.find_element(By.XPATH, "//mvid-carousel[contains(@class, 'carusel ng-star-inserted')]")

for num in range(int(number)):
    product_data = {}
    # print(num)
    title = products.find_elements(By.XPATH, ".//div[@class='title']//div")[num].get_attribute("textContent")
    # print(title)
    href = products.find_elements(By.XPATH, ".//div[@class='title']/a[@class='ng-star-inserted']")[num].get_attribute(
        "href"
    )
    # print(href)
    price = products.find_elements(By.XPATH, ".//span[@class='price__main-value']")[num].get_attribute("textContent")
    # print(int(price.replace("\xa0", "").strip()))

    product_data["_id"] = href
    product_data["href"] = href
    product_data["title"] = title
    product_data["price"] = int(price.replace("\xa0", "").strip())

    try:
        trend.insert_one(product_data)
    except DuplicateKeyError:
        print("Запись уже существует в БД")

driver.close()
print(f"Всего записей в коллекции: {len(list(db.trend.find()))}")
