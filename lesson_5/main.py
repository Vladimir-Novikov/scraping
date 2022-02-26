from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service

s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

driver.get('https://gb.ru/login')

elem = driver.find_element(By.ID, 'user_email')
elem.send_keys('study.ai_172@mail.ru')

elem = driver.find_element(By.ID, 'user_password')
elem.send_keys('Password172')

elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.XPATH, "//a[contains(@href, '/users/')]")
href = elem.get_attribute('href')
driver.get(href)

elem = driver.find_element(By.XPATH, "//a[contains(@href, '/users/')]")
href = elem.get_attribute('href')
driver.get(href)

elem = driver.find_element(By.CLASS_NAME, "text-sm")
href = elem.get_attribute('href')
driver.get(href)

print()
hours = driver.find_element(By.NAME, 'user[time_zone]')
select = Select(hours)
select.select_by_value("Tokyo")

hours.submit()

# driver.close()