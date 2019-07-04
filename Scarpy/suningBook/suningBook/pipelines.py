# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
from pymongo import MongoClient
import json

class SuningbookPipeline(object):
    def open_spider(self,spider):
        """spider开始时调用一次，可在此创建链接的monggo客户端:MongoClient!!!别再写错了"""
        client = MongoClient() # 本地客户端，无需host和port
        self.collection = client["SuNing"]["book"]

    def close_spider(self,spider):
        """spider开始时调用一次，可在此关闭链接的monggo客户端"""
        self.collection.close()

    def process_item(self, item, spider):
        # author ,book_name,publisher中间有多余的空白符
        item["author"] = re.sub(r"\s","",item["author"]) if item["author"] is not None else None
        item["book_name"] = re.sub(r"\s", "", item["book_name"]) if item["book_name"] is not None else None
        item["publisher"] = re.sub(r"\s", "", item["publisher"]) if item["publisher"] is not None else None
        # 按单个字典在yield生成
        file_path = "SuNing_BOOK.json"
        with open(file_path,"a",encoding="utf-8") as f:
            f.write(json.dumps(dict(item),ensure_ascii=False))
            f.write("\r\n")
        self.collection.insert_one(dict(item))





