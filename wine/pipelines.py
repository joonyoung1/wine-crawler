# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient


class WinePipeline:
    def process_item(self, item, spider):
        return item


class MongoDBPipeline:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['wine_db']
        self.db['wine_collection'].drop()

    def process_item(self, item, spider):
        self.db['wine_collection'].insert_one(dict(item))
        return item
