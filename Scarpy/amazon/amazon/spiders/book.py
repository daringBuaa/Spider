# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from amazon.items import AmazonItem
from copy import deepcopy
from urllib.parse import urljoin

class BookSpider(RedisCrawlSpider):
    """
    改变继承的父类为：RedisCrawlSpider
    取消start_url，改为在redis中插入，避免重复读取 lpush redis_key start_url
    设置redis_key= amazon
    """
    name = 'book'
    allowed_domains = ['amazon.cn']
    redis_key = "amazon_crawl"
    #start_urls = ['https://www.amazon.cn/%E5%9B%BE%E4%B9%A6/b/ref=sa_menu_top_books_l1?ie=UTF8&node=658390051']

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-one']/div/li//a"),
             callback='parse_vice_title', follow=False),
        # Rule(LinkExtractor(restrict_xpaths="//ul[@class='//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-two']/div/li//a"),
        #      callback='books_detail', follow=False),
        # Rule(LinkExtractor(restrict_xpaths="//div[@id='mainResults']/ul/li//a[@class='a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal']"),
        #      callback='more_detail', follow=False),
        # Rule(LinkExtractor(
        #     restrict_xpaths="//a[@id='pagnNextLink']"), # 单纯翻页
        #     follow=True),
    )


    def parse_vice_title(self,response):
        item = AmazonItem()
        li_list = response.xpath("//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-two']/div/li")
        for li in li_list:
            item["vice_title"] = li.xpath("./span/a/span/text()").extract_first()
            item["vice_title_url"] = "https://www.amazon.cn" + li.xpath("./span/a/@href").extract_first()
            item["vice_title_url"] = "https://www.amazon.cn" + li.xpath("./span/a/@href").extract_first()
            yield scrapy.Request(
                item["vice_title_url"],
                meta={"item": deepcopy(item)},
                callback=self.books_detail
            )

    def books_detail(self, response):
        item = response.meta["item"]
        li_list = response.xpath("//div[@id='mainResults']/ul/li")
        for li in li_list:
            item["book_name"] = li.xpath(".//h2/text()").extract_first()
            item["book_img"] = li.xpath(".//img/@src").extract_first()
            item["book_url"] = li.xpath(
                ".//a[@class='a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal']/@href").extract_first()
            item["author"] = li.xpath(".//div[@class='a-row a-spacing-small']/div[2]//text()").extract()
            item["price"] = li.xpath(
                ".//span[@class='a-size-base a-color-price s-price a-text-bold']/text()").extract_first()
            # 当前页无出版社信息
            yield scrapy.Request(
                item["book_url"],
                meta={"item": deepcopy(item)},
                callback=self.more_detail
            )
        # 翻页
        next_url = response.xpath("//a[@id='pagnNextLink']/@href").extract_first()  # 不完整
        next_url = urljoin(response.url, next_url)
        print(next_url)
        yield scrapy.Request(
            next_url,
            meta={"item": item},
            callback=self.books_detail
        )

    def more_detail(self, response):
        item = response.meta["item"]
        item["publisher"] = response.xpath("//div[@class='content']//li/b[text()='出版社:']/../text()").extract()
        yield item
