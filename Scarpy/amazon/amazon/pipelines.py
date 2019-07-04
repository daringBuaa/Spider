# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os

class AmazonPipeline(object):
    def process_item(self, item, spider):
        if spider.name =="book1":
            file_path = 'amazon/amazon_book.json'
            with open(file_path,"a",encoding="utf-8") as f:
                f.write(json.dumps(dict(item),ensure_ascii=False))
                f.write(os.linesep)
        else:
            file_path = 'amazon/amazon_book_crawl.json'
            print(item)
            with open(file_path,"a",encoding="utf-8") as f:
                f.write(json.dumps(dict(item),ensure_ascii=False))
                f.write(os.linesep)


