import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class LabirintSpider(scrapy.Spider):
    name = "labirint"
    allowed_domains = ["labirint.ru"]
    start_urls = [
        "https://www.labirint.ru/search/%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?stype=0"
    ]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@class='product-title-link']/@href").getall()
        full_links = ["https://www.labirint.ru" + url for url in links]
        for link in full_links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        url = response.url
        title = response.xpath("//h1/text()").get()
        authors = response.xpath("//div[contains(text(),'Автор:')]/a/text()").getall()
        old_price = response.xpath("//span[@class='buying-priceold-val-number']/text()").get()
        new_price = response.xpath("//span[@class ='buying-pricenew-val-number']/text()").get()
        rate = response.xpath("// div[@id ='rate']/text()").get()
        yield BookparserItem(url=url, title=title, authors=authors, old_price=old_price, new_price=new_price, rate=rate)
