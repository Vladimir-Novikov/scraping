from pprint import pprint
import requests
from lxml import html

url = 'https://ru.ebay.com/b/Fishing-Equipment-Supplies/1492/bn_1851047'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}

response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)

fishing_items = dom.xpath("//li[contains(@class,'s-item')]")

fishing_list = []
for item in fishing_items:
    fish = {}
    name = item.xpath(".//h3[@class='s-item__title']/text()")[0]
    link = item.xpath(".//h3[@class='s-item__title']/../@href")[0]
    price = item.xpath(".//span[@class='s-item__price']//text()")
    info = item.xpath(".//span[contains(@class,'s-item__hotness')]/span/text()")

    fish['name'] = name
    fish['price'] = price
    fish['info'] = info
    fish['link'] = link

    fishing_list.append(fish)

pprint(fishing_list)
