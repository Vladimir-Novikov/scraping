# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    user_data = scrapy.Field()
    _id = scrapy.Field()
