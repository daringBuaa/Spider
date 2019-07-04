import requests
from lxml import etree
from queue import Queue
import re
import json
from threading import Thread
import time
import gevent

class TianTianFundSpider(object):
    """
    天天基金网：每个交易日 16:00～23:00 更新当日的最新开放式基金净值 
    数据为json格式
    基金净值：href："http://fund.eastmoney.com/fund.html"
    总页数可在起始page中找到
    第一页：'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?&sort=zdf,desc&page=1,200&onlySale=0'
    """
    def __init__(self):
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        self.start_url = "http://fund.eastmoney.com/fund.html"
        self.url = "http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?&sort=zdf,desc&page={},200&onlySale=0"
        self.showday = None # 保存时间信息
        self.urlList_queue = Queue()
        self.content_queue = Queue()

    def get_url_list(self):
        response = requests.get(self.start_url,headers=self.header)
        element = etree.HTML(response.content)
        # 从结果中提取页数构造url地址list
        page_info = element.xpath("//div[@id='pager']/span[@class='nv'][1]/text()") # 共34页
        # 用正则取页码数
        pages = re.match(r"\D(\d*?)\D",page_info[0]).group(1)
        # 构造url列表，并使用队列存储解耦以及多线程/协程
        for i in range(int(pages)):
            url = self.url.format(i+1)
            self.urlList_queue.put(url)

    def get_content(self):
        while True:
            url = self.urlList_queue.get()
            print(url)
            response = requests.get(url,headers=self.header)
            # 得到的是var db{...}
            response_str = response.content.decode()[7:-1] #字符串
            # 切片后取需要的两个列表通过json转化
            str_list = response_str.split(":")
            response_list = list()
            response_list.append(json.loads(str_list[2][0:-6]))
            response_list.append(json.loads(str_list[8]))
            # print(len(response_list))

            # 对于基金数据时间很重要
            self.showday = response_list[1] # 包含前一天2019-4-17和前两天时间2019-4-16
            content_list = response_list[0]
            # print(content)# datas中为两个列表一个列表100条
            # # 最后一页可能只有一个列表，为避免报错
            # if len(content)==2:
            #     content_list = content[0] + content[1]
            # else:
            #     content_list = content[0]
            # # 提取数据（股票型）
            for fund in content_list: # 子元素为列表
                fund_content=list()
                # print(fund)
                # 基金序号
                fund_content.append(fund[14])
                # 基金代码
                fund_content.append(fund[0])
                # 基金名称
                fund_content.append(fund[1])
                # 前一天单位净值
                fund_content.append(fund[3])
                # 前一天累计净值
                fund_content.append(fund[4])
                # 前两天单位净值
                fund_content.append(fund[5])
                # 前两天累计净值
                fund_content.append(fund[6])
                # 日增长值
                fund_content.append(fund[7])
                # 日增长率
                fund_content.append(fund[8])
                # 申购状态
                fund_content.append(fund[9])
                # 赎回状态
                fund_content.append(fund[10])
                # 手续费
                fund_content.append(fund[11])
                self.content_queue.put(fund_content)
            # 使队列计数减一
            self.urlList_queue.task_done()

    def save_data(self):
        time.sleep(1)# 由于进程先进来的时候self.showday还未赋值，会导致表头确实时间，因此可以小睡一下
        file_path = "spider_data/天天基金.json"
        # 制作数据表头
        header= ["基金序号","基金代码","基金名称",self.showday[0]+"单位净值",self.showday[0]+"累计净值",
                 self.showday[1]+"单位净值",self.showday[1]+"累计净值",
                 "日增长值","日增长率","申购状态","赎回状态","手续费"]
        with open(file_path,"a",encoding="utf-8") as f:
            f.write(json.dumps(header,ensure_ascii=False))
            f.write("\r\n")
        # 保存数据
        print(header)
        while True:
            content=self.content_queue.get()
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(content, ensure_ascii=False))
                f.write("\r\n")
            self.content_queue.task_done()

    def main(self):
        thread_list=list()
        # 1.通过起始url发送请求
        thread1=Thread(target=self.get_url_list)
        thread_list.append(thread1)
        # 2.在响应中提取数据，下一页url
        thread2 = Thread(target=self.get_content)
        thread_list.append(thread2)
        # 3.保存数据，循环
        thread3 = Thread(target=self.save_data)
        thread_list.append(thread3)

        # 设置守护进程
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        time.sleep(1)
        for q in [self.urlList_queue, self.content_queue]:
            q.join()
        # 使用协程，spider
        # gevent.joinall([
        #     gevent.spawn(self.get_url_list),
        #     gevent.spawn(self.get_content),
        #     gevent.spawn(self.save_data)
        # ])
        # for q in [self.urlList_queue, self.content_queue]:
        #     q.join()

        print(self.urlList_queue.qsize(),self.content_queue.qsize())

if __name__ == '__main__':
    tiantian = TianTianFundSpider()
    tiantian.main()