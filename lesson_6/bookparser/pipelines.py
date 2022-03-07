# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient("127.0.0.1", 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):
        item['old_price'] = int(item['old_price'])
        item['new_price'] = int(item['new_price'])
        item['authors'] = ', '.join(item['authors'])
        item['rate'] = float(item['rate'])
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item
