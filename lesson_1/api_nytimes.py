import requests
import json
from pprint import pprint
from datetime import date

# Самыe просматриваемые статьи на NYTimes.com за последние 7 дней.


api_key = "****************"  # ключ как Вы говорили на уроке я убрал из этого файла
url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/7.json?api-key={api_key}"
response = requests.get(url)

j_data = json.loads(response.text)  # переводим в json, для удобной работы ключ - значение

if response.ok:  # если OK то выполняем вывод данных и запись в json
    article_dict = {}
    article_list = []
    result = j_data.get("results")
    for number, item in enumerate(result, 1):
        article_dict[item.get("title")] = item.get("url")  # добавляем данные в словарь
        article_list.append(item.get("title"))
        print(number, item.get("title"), item.get("url"))
    article_dict["article_list"] = article_list

    # пишем в json файл с текущей датой следующие данные: список всех статей; название статьи: ссылка на статью.
    # чтобы можно было по ключу (название) получить url и перейти к просмотру статьи
    current_date = date.today()
    with open(f"mostpopular_{current_date}.json", "w", encoding="utf-8") as file:
        json.dump(article_dict, file)

    # раскомментировать данный код, если нужно прочитать созданный файл json
    # with open(f'mostpopular_{current_date}.json', 'r', encoding='utf-8') as file:
    #     json_data = json.load(file)
    #     pprint(json_data)

else:
    print("Сервер недоступен / указан неверный ключ")
