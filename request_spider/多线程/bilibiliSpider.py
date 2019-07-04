# coding = "utf-8"
import requests
import json
from queue import Queue
from threading import Thread
import math
import time
import pandas

class BiLiSpider(object):
    def __init__(self,av_number):
        # 文件位于https://api.bilibili.com/x/v2/reply?pn=4&type=1&oid=14184325
        # 翻页后https://api.bilibili.com/x/v2/reply?&pn=5&type=1&oid=14184325
        # 返回为json
        # sort 为弹幕排序方式：0楼层逆序，全部评论，2 按热度排序
        # pn 表示弹幕页码
        # oid：为视频av号码
        # type：1表示可以评论，2表示禁止评论
        self.number = av_number
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        self.start_url = "https://api.bilibili.com/x/v2/reply?&pn={}&type=1&oid="\
                         +av_number+"&sort=2"
        self.url_queue = Queue()
        self.response_queue = Queue()
        self.content_queue = Queue()

    def get_url_queue(self):
        # 1.准备起始url
        url = self.start_url.format(1)
        print(url)
        response = requests.get(url, headers=self.header)  # 返回一个json
        res_str = response.content.decode() # 将响应转为str
        html_dict = json.loads(res_str)
        # 获取总的祝评论数count,num(总页数),size(每页条数),总评论account
        # pages = html_dict["data"]["page"]["num"] # 此为当前页数
        count = html_dict["data"]["page"]["count"]
        size = html_dict["data"]["page"]["size"]
        pages = math.ceil(count/size)
        print(count,size,pages)
        # 构造url列表
        for i in range(pages):
            self.url_queue.put(self.start_url.format(i+1))
        # print(self.url_queue.qsize())

    def get_response_queue(self):
        while True:
            url = self.url_queue.get()
            #print(url) # 并未重复取url
            response = requests.get(url, headers=self.header)
            html_dict = json.loads(response.content.decode())
            self.response_queue.put(html_dict)
            # 调用task_done使队列计数减一
            self.url_queue.task_done()

    def get_content_queue(self):
        while True:
            html_dict = self.response_queue.get()
            for view in html_dict["data"]["replies"]:
                # 最终数据以csv的形势存储，因此，得一列表的形势保存
                content = list()
                # 楼层数 content["floor"]=view["content"]["floor"]
                content.append(view["floor"])
                # 用户id content["user_id"] = view["member"]["mid"]
                content.append(view["member"]["mid"])
                # 用户名 content["user_name"] = view["member"]["uname"]
                content.append(view["member"]["uname"])
                # 用户性别 content["user_sex"] = view["member"]["sex"]
                content.append(view["member"]["sex"])
                # 评论内容 content["main_review"] = view["content"]["message"]
                content.append(view["content"]["message"])
                # 评论点赞数 content["likes"] = view["content"]["like"]
                content.append(view["like"])
                # 评论回复数 content['r_count'] = view["content"]["rcount"]
                content.append(view["rcount"])
                ctime = view["ctime"] # 为编码后的秒杀，需要转化
                time_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ctime))
                content.append(time_str)
                print(content)
                self.content_queue.put(content)
            # 队列引用计数-1
            self.response_queue.task_done()

    def save_content(self):
        # 构造csv表头
        csv_header = ["楼层","用户ID","用户名","性别","评论内容","点赞数","回复数","评论时间"]
        file_name = "哔哩哔哩视频号：全职高手评论.json"#%self.number
        with open(file_name,"w",encoding="utf-8") as f:
            f.write(json.dumps(csv_header,ensure_ascii=False))
            f.write("\r\n")
        # dataframe = pandas.DataFrame(csv_header)
        # dataframe.to_csv(file_name,mode="a",index=False,sep=",",header=True,encoding="utf-8")

        # 写入爬取的内容,使用json转化数据类型，则只能用于写入json，否则会乱码
        while True:
            content_list = self.content_queue.get()
            print(content_list)
            with open(file_name,"a",encoding="utf-8") as f:
                f.write(json.dumps(content_list,ensure_ascii=False))
                f.write("\r\n")
            # dataframe = pandas.DataFrame(content_list)
            # dataframe.to_csv(file_name, mode="a", index=False, header=False,encoding="utf-8")
            # 计数减一
            self.content_queue.task_done()

    def main(self):
        # 设置多线程作业
        thread_list = []
        # 2. 获取总页数，为解耦以及多线程，使用队列
        # self.get_url_queue(url)
        t1 =Thread(target=self.get_url_queue)
        thread_list.append(t1)

        # 3. 发送请求，获取响应，存放于响应队列中;由于请求比较耗时，因此可用多个线程
        for i in range(1): # 此时若为多线程则可能打乱写入顺序
            t = Thread(target=self.get_response_queue)
            thread_list.append(t)

        # 4 get _content
        for i in range(1): # 此时若为多线程则可能打乱写入顺序
            t = Thread(target=self.get_content_queue)
            thread_list.append(t)

        # 4. 提取数据，存放于内容队列中
        t3 = Thread(target=self.save_content)
        thread_list.append(t3)

        # 5.设置守护进程使子进程退出循环,即主进程结束，子进程结束
        for t in thread_list:
            t.setDaemon(True)
            t.start()

        time.sleep(2)
        print(self.url_queue.qsize(),self.response_queue.qsize(),self.content_queue.qsize())

        # 6 利用队列堵塞主进程
        for q in [self.url_queue,self.response_queue,self.content_queue]:
            q.join() # 没有阻塞住！！！
        print("主进程结束")

if __name__ == '__main__':
    # av14184325 = BiLiSpider("14184325")
    # av14184325.main()
    quanzhigaoshou = BiLiSpider("9659814")
    quanzhigaoshou.main()

