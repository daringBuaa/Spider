# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SuningbookItem(scrapy.Item):
    # define the fields for your item here like:
    # 需存储大标题，大标题url，小标题，小标题url，书名，url,封面，简介，作者，出版社，价格
    main_title = scrapy.Field()
    main_title_url = scrapy.Field()
    vice_title = scrapy.Field()
    vice_title_url = scrapy.Field()
    book_name = scrapy.Field()
    book_url = scrapy.Field()
    book_img = scrapy.Field()

    author = scrapy.Field()
    publisher = scrapy.Field()
    price = scrapy.Field()
    published_time = scrapy.Field()


