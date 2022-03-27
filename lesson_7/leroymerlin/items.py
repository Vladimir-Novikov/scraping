# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose


def get_price(price_list):
    # цены есть без копеек (напр вазы), есть с копейками (напр ламинат)
    if len(price_list) == 4:
        try:
            price = int(price_list[0].replace(' ', '')) + int(price_list[1].replace(' ', ''))/100
            return price
        except Exception:
            return price_list
    elif len(price_list) == 3:
        try:
            price = float(price_list[0].replace(' ', ''))
            return price
        except Exception:
            return price_list
    else:
        return price_list


def spec_value_proc(spec_list):
    result = spec_list.replace('\n', '').strip()
    return result


class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field(output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    specifications = scrapy.Field()
    _id = scrapy.Field()
    spec_key = scrapy.Field()
    spec_value = scrapy.Field(input_processor=MapCompose(spec_value_proc))
    price = scrapy.Field(input_processor=Compose(get_price), output_processor=TakeFirst())
