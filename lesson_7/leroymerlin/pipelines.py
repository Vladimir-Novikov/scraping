# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import hashlib
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient("127.0.0.1", 27017)
        self.mongobase = client.products

    def process_item(self, item, spider):
        # создание словаря с характеристиками и удаление не нужных данных
        item['specifications'] = dict(zip(item['spec_key'], item['spec_value']))
        item.pop('spec_key', None)
        item.pop('spec_value', None)
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for photo in item['photos']:
                try:
                    yield scrapy.Request(photo)
                except Exception as err:
                    print(err)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        # создание папок с изображениями по имени товара
        image_guid = hashlib.sha1(request.url.encode()).hexdigest()
        path_name = item['title']
        rep = ['"', "?", "*", "/", "\\", ":", ">", "<", "|"]
        for item in rep:
            if item in path_name:
                path_name = path_name.replace(item, "_")
        return f"{path_name}/{image_guid}.jpg"
