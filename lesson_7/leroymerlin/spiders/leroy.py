import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://leroymerlin.ru/search/?q={kwargs.get('search')}"]


    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='product-name']")
        for link in links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('title', "//h1/text()")
        loader.add_xpath('price', "//uc-pdp-price-view[@slot='primary-price']/span/text()")
        loader.add_xpath('currency', "//span[@slot='currency']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('photos', "//source[contains(@media, '(min-width: 1024px)')]/@srcset")
        loader.add_xpath('spec_key', "//section[@id='nav-characteristics']//dt/text()")
        loader.add_xpath('spec_value', "//section[@id='nav-characteristics']//dd/text()")
        yield loader.load_item()

        # title = response.xpath("//h1/text()").get()
        # price = response.xpath("//span[@slot='price']/text()").get()
        # currency = response.xpath("//span[@slot='currency']/text()").get()
        # url = response.url
        # photos = response.xpath("//source[contains(@media, '(min-width: 1024px)')]/@srcset").getall()
        # yield LeroymerlinItem(title=title, price=price, currency=currency, url=url, photos=photos)
