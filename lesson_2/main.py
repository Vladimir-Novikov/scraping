import requests
from bs4 import BeautifulSoup
from pprint import pprint

url = 'http://127.0.0.1:5000/'

response = requests.get(url)

dom = BeautifulSoup(response.text, 'html.parser')

tag_a = dom.find('a')
# print(tag_a.getText())

parent_a = tag_a.parent.parent
# print(parent_a)

children_div = parent_a.findChildren(recursive=False)
# pprint(list(children_div))

div_d = dom.find('div', {'id': 'd'})
# pprint(div_d)

tags_p = dom.find_all('p', {'class': 'paragraph'})
# pprint(tags_p)

tags_red_p = dom.find_all('p', {'class': 'red paragraph'})
# pprint(tags_red_p)

tags_red_p = dom.find_all('p', {'class': ['red', 'paragraph']})
# pprint(tags_red_p)

tags_red_p = dom.select('p.red.paragraph')
# pprint(tags_red_p)

p6 = dom.find(text='РЁРµСЃС‚РѕР№ РїР°СЂР°РіСЂР°С„')
pprint(p6.parent)