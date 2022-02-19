# e5e4cd692a72b0b66ea0a6b80255d1c3
import requests
import json
from pprint import pprint

city = "Arzamas"

url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=e5e4cd692a72b0b66ea0a6b80255d1c3"

response = requests.get(url)
# print(response.headers.get('Content-Type'))
j_data = response.json()
# pprint(j_data)


print(f'В городе {j_data.get("name")} сейчас {j_data.get("main").get("temp") - 273.15} градусов')