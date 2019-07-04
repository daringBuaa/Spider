# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
from copy import deepcopy
from amazon.items import AmazonItem
from scrapy_redis.spiders import RedisSpider


class Book1Spider(RedisSpider):
    """使用scrapy_redis 实现分布式，增量式爬虫
    settings 中加入4条设置
    1.DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter" # 过滤方式
    2.SCHEDULER = "scrapy_redis.scheduler.Scheduler" #requests 队列
    3.SCHEDULER_PERSIST = True # 是否持久化储存
    4. 设置 REDIS_URL = "redis://127.0.0.1:6379" # ip+默认端口6379
    更改父类 redisSpider
    不设置start_url 避免重复取start_url lpush amazon start_url
    设置redis_key = "amazon"
    """
    name = 'book1'
    allowed_domains = ['amazon.cn']
    #start_urls = ['https://www.amazon.cn/%E5%9B%BE%E4%B9%A6/b/ref=sa_menu_top_books_l1?ie=UTF8&node=658390051']
    redis_key = "amazon"

    def parse(self, response):
        # 提取大分类：分组、遍历
        li_list = response.xpath("//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-one']/div/li")
        for li in li_list:
            item = AmazonItem()
            item["main_title"] = li.xpath(".//a/span/text()").extract_first()
            item["main_title_url"] = li.xpath(".//a/@href").extract_first()
            item["main_title_url"] = urljoin(response.url,item["main_title_url"])
            # 请求列表页
            yield scrapy.Request(
                item["main_title_url"],
                meta={"item":deepcopy(item)},
                callback=self.vice_title_list
            )

    def vice_title_list(self,response):
        item = response.meta["item"]
        li_list = response.xpath("//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-two']/div/li")
        for li in li_list:
            item["vice_title"] = li.xpath("./span/a/span/text()").extract_first()
            item["vice_title_url"] = "https://www.amazon.cn" + li.xpath("./span/a/@href").extract_first()
            yield scrapy.Request(
                item["vice_title_url"],
                meta={"item":deepcopy(item)},
                callback=self.books_detail
            )

    def books_detail(self,response):
        item =response.meta["item"]
        li_list = response.xpath("//div[@id='mainResults']/ul/li")
        for li in li_list:
            item["book_name"] = li.xpath(".//h2/text()").extract_first()
            item["book_img"] = li.xpath(".//img/@src").extract_first()
            item["book_url"] = li.xpath(".//a[@class='a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal']/@href").extract_first()
            item["author"] = li.xpath(".//div[@class='a-row a-spacing-small']/div[2]//text()").extract()
            item["price"] = li.xpath(".//span[@class='a-size-base a-color-price s-price a-text-bold']/text()").extract_first()
            # 当前页无出版社信息
            yield scrapy.Request(
                item["book_url"],
                meta={"item":deepcopy(item)},
                callback=self.more_detail
            )
        # 翻页
        next_url = response.xpath("//a[@id='pagnNextLink']/@href").extract_first() # 不完整
        next_url = urljoin(response.url,next_url)
        print(next_url)
        yield scrapy.Request(
            next_url,
            meta={"item":item},
            callback=self.books_detail
        )

    def more_detail(self,response):
        item = response.meta["item"]
        item["publisher"] = response.xpath("//div[@class='content']//li/b[text()='出版社:']/../text()").extract()
        yield item

