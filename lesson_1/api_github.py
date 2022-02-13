import requests
import json
from pprint import pprint

username = "Vladimir-Novikov"  # указываем username
url = f"https://api.github.com/users/{username}/repos"
response = requests.get(url)

j_data = json.loads(response.text)  # переводим в json, для удобной работы ключ - значение
if response.ok:  # если указанный юзер существует (получаем не 404) то выполняем вывод данных и запись в json
    print(f"Список репозиториев пользователя: {username}", "\n")
    repo_dict = {}
    repo_list = []
    repo_dict["username"] = username
    for number, item in enumerate(j_data, 1):
        repo_dict[item.get("name")] = item.get("html_url")  # добавляем данные в словарь Репозиторий - url
        repo_list.append(item.get("name"))
        print(number, item.get("name"), item.get("html_url"))
    repo_dict["repo_list"] = repo_list  # список всех репозиториев

    # пишем в json файл с именем юзера следующие данные: список всех репо; репо: ссылка на репо; юзернэйм.
    # можно посмотреть список всех репозиториев, и получить ссылку на конкретный по ключу.
    with open(f"{username}.json", "w", encoding="utf-8") as file:
        json.dump(repo_dict, file)

    # раскомментировать данный код, если нужно прочитать созданный файл json
    # with open(f"{username}.json", "r", encoding="utf-8") as file:
    #     json_data = json.load(file)
    #     pprint(json_data)

else:
    print(f"Пользователь {username} не найден")
