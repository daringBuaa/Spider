import requests
import json
from queue import Queue
from lxml import etree
from threading import Thread
import time
import re

class QQMusicSpider(object):
    """
    巅峰榜流行指数："https://y.qq.com/n/m/detail/toplist/index.html?ADTAG=myqq&from=myqq&id=4"
    巅峰欧美id=3，巅峰流行4，内地5，港台6 
    热歌榜：”https://y.qq.com/n/m/detail/toplist/index.html?ADTAG=myqq&from=myqq&channel=10007100&id=26
    热歌26，新歌27
    "获取id列表"："https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg?"json--
    但有一个jsoncallback需添加一个参数format=json
    """
    """
    歌单：获取对应id："https://c.y.qq.com/musichall/fcgi-bin/fcg_yqqhomepagerecommend.fcg?_=1555550164179&format=json"
    https://y.qq.com/n/m/detail/taoge/index.html?ADTAG=myqq&from=myqq&channel=10007100&id=2043041547
    https://y.qq.com/n/m/detail/taoge/index.html?ADTAG=myqq&from=myqq&channel=10007100&id=2040362185
    https://c.y.qq.com/musichall/fcgi-bin/fcg_yqqhomepagerecommend.fcg?&format=json
    """
    def __init__(self):
        self.header = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}
        self.top_list_get_id_url = "https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg?format=json"
        #self.taoge_get_id_url = "https://c.y.qq.com/musichall/fcgi-bin/fcg_yqqhomepagerecommend.fcg?_=1555550164179&format=json"
        self.get_toplist_url = "https://y.qq.com/n/m/detail/toplist/index.html?ADTAG=myqq&from=myqq&id={}"
        #self.get_playlist_url = "https://y.qq.com/n/m/detail/taoge/index.html?ADTAG=myqq&from=myqq&id={}"
        self.topList_queue = Queue()
        #self.playList_queue = Queue()
        self.topList = Queue()
        #self.palyList = Queue()

    def get_top_list_url(self):
        response = requests.get(self.top_list_get_id_url, headers=self.header)
        html_str = response.content.decode()
        # 提取各个排行榜列表与对应id
        top_lists = json.loads(html_str)["data"]["topList"]
        for content_dic in top_lists:
            top_list_dict = dict()
            top_list_dict["name"] = content_dic["topTitle"]
            top_list_dict["listenCount"] = content_dic["listenCount"]
            top_list_dict["url"] = self.get_toplist_url.format(content_dic["id"])
            self.topList_queue.put(top_list_dict)

    # def get_paly_list_url(self):
    #     response = requests.get(self.taoge_get_id_url,headers=self.header)
    #     html_str = response.content.decode()
    #     # 提取各个推荐歌单与对应id
    #     top_lists = json.loads(html_str)["data"]["songList"]
    #     for content_dic in top_lists:
    #         top_list_dict=dict()
    #         top_list_dict["name"] = content_dic["songListDesc"]
    #         top_list_dict["author"] = content_dic["songListAuthor"]
    #         top_list_dict["accessnum"] = content_dic["accessnum"]
    #         top_list_dict["url"] = self.get_playlist_url.format(content_dic["id"])
    #         self.playList_queue.put(top_list_dict)

    def get_topList(self):
        while True:
            list_info = self.topList_queue.get()
            url = list_info["url"]
            response =requests.get(url,headers=self.header)
            element = etree.HTML(response.content.decode())
            # 分组：获取包含歌曲信息的各个li标签
            # !!!!!xpath取出的均为列表
            total_num = element.xpath("//div[@class='count_box__desc']/span/text()")
            num = total_num[0] if len(total_num)>0 else " "
            list_info["total"] = num
            # 将字典转化为list
            total_content = [list(list_info.values()),["排名序号", "排名指数", "歌名", "歌手"]]
            li_list = element.xpath("//li[@class='js_play_song qui_list__item']")
            # 遍历：
            for li in li_list:
                content=list()
                content.append(li.xpath(".//span[@class='qui_list__decimal']/text()")[0]) # sortNum
                rank = li.xpath(".//span[@class='rank_trend__number']/text()")
                content.append(rank[0] if len(rank)>0 else "0") #rank_trend_number
                # 歌曲名与歌手名前后有很多换行符与空格，可用正则表达式去除
                song_name = li.xpath(".//h3/span/text()")[0]
                content.append(re.match(r'\s*(.*)\r\s*',song_name).group(1)) # song_name
                singer = li.xpath(".//p/span/text()")[0]
                content.append(re.match(r'\s*(.*)\r\s*',singer).group(1)) # singer
                total_content.append(content)
            # 每个排行榜存为一个list放入总的队列
            self.topList.put(total_content)
            self.topList_queue.task_done()

    def save(self):
        while True:
            topList = self.topList.get()
            # 列表第一个元素为歌单详细信息
            # 列表第二个元素为字段信息，排名序号", "排名指数", "歌名", "歌手"
            # 之后为每首歌的信息,每个为一个列表元素
            filepath= "./spider_data/QQ音乐巅峰榜.json"
            with open(filepath,'a',encoding="utf-8") as f:
                for info in topList:
                    f.write(json.dumps(info,ensure_ascii=False))
                    f.write("\r\n")
            with open(filepath, 'a', encoding="utf-8") as f:
                f.write("\r\n")
            print("%s保存完成"%topList[0][0])
            self.topList.task_done()

    def main(self):
        thread_list = list()
        # 获取排行榜url及信息
        thread_get_url = Thread(target=self.get_top_list_url)
        thread_list.append(thread_get_url)
        # 获取推荐歌单url及信息
        # self.get_play_list_url()
        # 提取各个歌单的歌曲信息，只获取了排行榜的歌曲信息，因为推荐个蛋的歌曲信息需要点击加载更多
        # 此时可以考虑使用selenium 和chromedriver
        thread_get_toplist = Thread(target=self.get_topList)
        thread_list.append(thread_get_toplist)
        # 保存数据
        thread_save_toplist = Thread(target=self.save)
        thread_list.append(thread_save_toplist)
        # 设置守护进程，使主进程结束，子进程循环结束
        for t in thread_list:
            t.setDaemon(True)
            t.start()

        # 来不及写入队列，主进程就执行完了？？
        time.sleep(2)

        # 使用队列堵塞主进程
        for q in [self.topList_queue,self.topList]:
            q.join()

        print("Completed!!")

if __name__ == '__main__':
    qq = QQMusicSpider()
    qq.main()