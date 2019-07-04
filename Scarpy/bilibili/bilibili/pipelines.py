# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from pymongo import MongoClient

class BilibiliPipeline(object):
    """
    可用于在此开启和关闭数据库客户端
    """
    def process_item(self, item, spider):
        print(item)
        #file_path = "bilibili/狐妖小红娘弹幕.json"
        # with open(file_path,"a",encoding="utf-8") as f:
        #     f.write(json.dumps(dict(item),ensure_ascii=False)) # item是类字典形势
        #     f.write(os.linesep)
        # self.collection.insert_one(dict(item))

    def open_spider(self,spider):
        self.client = MongoClient() # 本地不需要穿地址与端口
        self.collection = self.client["bilibili"]["foxgirl"]

    def close_spider(self,spider):
        self.client.exit




