# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    main_title = scrapy.Field()
    main_title_url = scrapy.Field()
    vice_title = scrapy.Field()
    vice_title_url = scrapy.Field()
    book_name = scrapy.Field()
    book_img = scrapy.Field()
    book_url = scrapy.Field()
    author = scrapy.Field()
    price = scrapy.Field()
    publisher = scrapy.Field()

