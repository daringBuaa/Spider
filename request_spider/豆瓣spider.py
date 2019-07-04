import json
import requests
from pymongo import MongoClient

class DouBanSpider(object):
    def __init__(self,type,tag):
        self.headers = {"User_Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) "
                                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                                     "Chrome/72.0.3626.121 Safari/537.36"}

        self.url = "https://movie.douban.com/j/search_subjects?"
        self.type = type
        self.tag = tag
        # 创建与mong交互的客户端，并用spider库下的douban集合
        client = MongoClient()# 本地可以不写(host="127.0.0.1",port=27017)
        self.collection = client["spider"]["douban"]

    def get_response(self,page_num):
        # "https://movie.douban.com/j/search_subjects?type=movie&"+
          # "tag="热门"&sort=recommend&page_limit=20&page_start=0"
        params = {"type": self.type, "tag": self.tag,"sort": "recommend","page_limit": 20,
                  "page_start": 20*page_num} # page_start = 20 *n
        response = requests.get(self.url,params=params,headers=self.headers)
        return json.loads(response.content.decode())

    def save(self,response_dict):
        # file_path = "spider_data/豆瓣%s(%s).json" % (self.type, self.tag)
        # with open(file_path, "a",encoding="utf-8") as f:
        #     # 将数据逐条写入文件中
        #     for content in response_dict["subjects"]:
        #         f.write(json.dumps(content, ensure_ascii=False))  # 转为字符串写入
        #         f.write("\r\n")  # 换行输入
        #         # print(len(response_dict["subjects"]))
        self.collection.insert_many(response_dict) # inser被弃用了，使用insert_one()/insert_many()

    def run(self):
        # 1.获取目标url地址
        page_num = 0
        while True:
            response_dict = self.get_response(page_num)
            # 2.保存数据
            self.save(response_dict)
            print("\r豆瓣%s(%s)第%d页Spider完成" % (self.type, self.tag, page_num + 1), end="")
            if len(response_dict["subjects"])< 20:
                print("Spider 完成")
                return
            page_num += 1

if __name__ == '__main__':
    # movies = DouBanSpider("movie","热门")
    # movies.run()
    # type = input("请输入要爬取的类型(movie、tv..)")
    movies = DouBanSpider("movie", "豆瓣高分")
    movies.run()
