# -*- coding: utf-8 -*-
import scrapy
import re
from bilibili.items import BilibiliItem
from scrapy_redis.spiders import RedisSpider


class PoptextSpider(RedisSpider):
    """
    "epList":包含所有视频的ep_id,aid等信息
    https://www.bilibili.com/bangumi/play/ep63873 # 每次更改后面ep_id
    或者www.bilibili.com/video/av2484334 更改aid
    弹幕：https://comment.bilibili.com/{3889896}.xml 更换cid
    "分布式”
    """
    name = 'poptext'
    allowed_domains = ['bilibili.com']
    # start_urls = ['https://www.bilibili.com/bangumi/play/ep63725']
    redis_key = "bili"

    def parse(self, response):
        """获取ep_id列表、cid列表"""
        # 正则时注意空白字符,内部应关闭贪婪，否会多去
        epList_str = re.findall(r"\"epList\":\s*\[(.*?)\],",response.body.decode(),re.DOTALL)[0]
        # with open("str.html","w") as f:
        #     f.write(epList_str)
        ep_id_list = re.findall(r",\"id\":\s*(.*?),",epList_str,re.DOTALL)
        cid_list = re.findall(r"\"cid\":\s*(.*?),",epList_str,re.DOTALL)
        # 总共104集
        pop_url ="https://comment.bilibili.com/{}.xml"
        av_url = "https://www.bilibili.com/bangumi/play/ep{}"
        for cid in cid_list:
            item =BilibiliItem()
            item["av_url"] = av_url.format(ep_id_list[cid_list.index(cid)])
            url = pop_url.format(cid)
            yield scrapy.Request(
                url,
                callback= self.detail,
                meta={"item":item}
            )

    def detail(self,response):
        item = response.meta["item"]
        item["content"] = response.xpath("//d/text()").extract()
        yield item


