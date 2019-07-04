# -*- coding: utf-8 -*-
import scrapy
from suningBook.items import SuningbookItem
import re
from copy import deepcopy


class BookSpider(scrapy.Spider):
    name = 'book'
    allowed_domains = ['https://book.suning.com/']
    start_urls = ['https://book.suning.com/'] # 包含所需信息，因此可做为start_url

    def parse(self, response):
        # 获取大分类名，及对应小分类的url地址(小分类也在列表页，因此可直接获取，减少请求
        total_outer_list = response.xpath("//div[@class='menu-item']//dt")
        # 需存储大标题，大标题url，小标题，小标题url，书名，封面，简介，作者，出版社，价格
        item = SuningbookItem()
        for dt in total_outer_list:
            item["main_title"] = dt.xpath(".//a/text()").extract_first()
            item["main_title_url"] = dt.xpath(".//a/@href").extract_first()
            # 小标题在于dt平级的dd中
            dd_list = dt.xpath("./../dd")
            for dd in  dd_list:
                item["vice_title"] = dd.xpath("./a/text()").extract_first()
                item["vice_title_url"] = dd.xpath("./a/@href").extract_first()
                # 进入小标题详情页：
                # print(item) 第一层ok！
                # 直接传item会在多进程中收到影响
                yield scrapy.Request(
                    item["vice_title_url"],
                    callback=self.parse_detail,
                    dont_filter=True,
                    meta={"item":deepcopy(item)}
                )

    def parse_detail(self,response):
        # 获取存储单元 item=deepcopy(response.meta["item"]),则下方可传递response.meta["item"]
        item = response.meta["item"]
        # print(response.request.url)
        li_list = response.xpath("//div[@id='filter-results']//li") # 只能娶到30
        # print(len(li_list))
        for li in li_list:
            item["book_name"] = li.xpath(".//p[@class='sell-point']/a/text()").extract_first()
            item["book_url"] = "https:"+ li.xpath(".//p[@class='sell-point']/a/@href").extract_first()
            # book_img由ajax加载，可以放在详情页中加载,价格也为ajax动态加载jsonp
            #print(item["book_url"])
            #item["book_img"] = "https:"+li.xpath(".//div[@class='img-block']/a/img/@src").extract_first()
            # price_content = li.xpath(".//p[@class='prive-tag']/em/text()")
            # #item["price"] = "".join(price_content)
            # print(len(price_content))
            # print(item["price"])

            yield scrapy.Request(
                item["book_url"],
                callback=self.book_detail,
                meta={"item":deepcopy(item)},
                dont_filter=True
            )
        # 构造下一页url地址,此时是否需要传递meta？不传第二轮之后，找不到item，会报错，item键都有值，循环时覆盖？
        # 下一页的url地址并不在标签中，response与element不同
        # next_url = "https://list.suning.com"+response.xpath("//a[@id='nextPage']/@href").extract_first()
        # print(next_url)
        # url = https://list.suning.com/1-502320-{}-0-0-0-0-14-0-4.html,0开始
        # page_info= response.xpath("//span[@class='page-more']/text()").extract_first() #共100页，到第,页
        # page_number = int(str(page_info)[1:-4]) # 获取总页数，可直接在response中获取
        url = "https://list.suning.com/1-502320-{}-0-0-0-0-14-0-4.html"
        currentPage = int(re.findall(r"param.currentPage = \"(.*?)\";",response.body.decode())[0])
        pageNumbers = int(re.findall(r"param.pageNumbers = \"(.*?)\";", response.body.decode())[0])
        while currentPage < pageNumbers-1:
            currentPage += 1
            next_url = url.format(currentPage)
            print(next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_detail,
                meta={"item": item}
            )

    def book_detail(self,response):
        item = response.meta["item"]
        # img的后缀为2.jpg_400w_400h_4e，取出后面尺寸信息[:-13]
        item["book_img"] = "https"+ response.xpath("//a[@id='bigImg']/img/@src").extract_first()[:-13]
        item["author"] = response.xpath("//ul[@class='bk-publish clearfix']/li[1]/text()").extract_first()
        item["publisher"] = response.xpath("//ul[@class='bk-publish clearfix']/li[2]/text()").extract_first()
        item["published_time"] = response.xpath("//ul[@class='bk-publish clearfix']/li[3]/span[2]/text()").extract_first()
        # autos = response.xpath("//span[@class='mainprice']//text()")
        # print(autos)
        # item["price"] = "".join(autos) # 将列表以""相连
        # 找一个定价聊以慰藉"itemPrice": "93.00",\转义",来匹配
        # 正则时注意空格
        price = re.findall(r"\"itemPrice\":\"(.*?)\",",response.body.decode())
        item["price"] = price[0] if len(price)>0 else None
        yield item




