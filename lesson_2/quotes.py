import requests
from bs4 import BeautifulSoup
from pprint import pprint

# пример с урока

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
}
base_url = "https://quotes.toscrape.com"
url = "https://quotes.toscrape.com"

quotes_list = []


response = requests.get(url, headers=headers)
if response.ok:
    dom = BeautifulSoup(response.text, "html.parser")
quotes = dom.find("div", {"class": "quote"})


while True:
    response = requests.get(url, headers=headers)
    if response.ok:
        dom = BeautifulSoup(response.text, "html.parser")
        quotes = dom.find_all("div", {"class": "quote"})

        for quote in quotes:
            quote_data = {}
            quote_text = quote.find("span").getText()

            author_data = quote.find("small")
            author_name = author_data.getText()
            author_link = base_url + author_data.findNextSibling()["href"]
            tags = quote.find_all("a", {"class": "tag"})
            tag_dict = {}
            for tag in tags:
                tag_dict[tag.getText()] = base_url + tag["href"]

            quote_data["text"] = quote_text
            quote_data["author"] = author_name
            quote_data["author_link"] = author_link
            quote_data["tags"] = tag_dict

            quotes_list.append(quote_data)
        next_page = dom.find("li", {"class": "next"})
        if next_page:
            url = base_url + next_page.find("a")["href"]
        else:
            break
    else:
        break

pprint(quotes_list)
print(len(quotes_list))
