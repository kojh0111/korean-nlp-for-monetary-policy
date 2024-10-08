# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YonhapNewsItem(scrapy.Item):
    title = scrapy.Field()
    press = scrapy.Field()
    content = scrapy.Field()
    reg_date = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
