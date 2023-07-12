# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WineItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    winery = scrapy.Field()
    name = scrapy.Field()
    region = scrapy.Field()
    rating = scrapy.Field()
    price = scrapy.Field()
    taste = scrapy.Field()
    flavor = scrapy.Field()
    reviews = scrapy.Field()
    pass
