import requests

url = 'http://google.ru'

response = requests.get(url)

if response.status_code == 200:
    pass

if response.ok:
    pass

response.headers
response.text
response.content

response.history

print()