# coding=utf-8
from selenium import webdriver
from queue import  Queue
import json
from threading import Thread


class WangYiYunSpider(object):
    """考虑到数据嵌套在iframe中，因此考虑是用sele+webdriver"""
    def __init__(self):
        self.start_url = "https://music.163.com/#/discover/playlist/?cat=华语"
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"}
        self.driver = webdriver.Chrome() # 实例化浏览器
        self.play_dict_queue = Queue()
        self.detail_queue = Queue()

    def parse_url(self):
        self.driver.get(self.start_url)
        self.driver.switch_to.frame("g_iframe")# 输入iframe的id或者name
        li_list = self.driver.find_elements_by_xpath("//ul[@id='m-pl-container']/li")
        # print(len(li_list))
        for li in li_list:
            play_dict = dict()
            play_dict["title"] = li.find_element_by_xpath("./div/a").get_attribute("title")
            play_dict["href"] =li.find_element_by_xpath("./div/a").get_attribute("href")
            play_dict["img"] = li.find_element_by_xpath("./div/img").get_attribute("src")
            self.play_dict_queue.put(play_dict)
        # self.driver.close()

    def get_detail(self):
        """详情页数据仍在iframe中"""
        while True:
            play_dict = self.play_dict_queue.get()
            print(play_dict["href"])
            # # 打开新窗口
            # newwindow = 'window.open("https://www.baidu.com");'
            # self.driver.execute_script(newwindow)
            # # 切换到新的窗口,这样不能多线程，必须等一个页面处理完才可以离开
            # handles = self.driver.window_handles
            # self.driver.switch_to_window(handles[-1])
            # web = webdriver.Chrome()
            self.driver.get(play_dict["href"])
            self.driver.switch_to.frame("g_iframe")
            content_dict = dict()
            content_list = list()
            content_dict["title"] = play_dict["title"]
            content_dict["img"] = play_dict["img"]
            content_dict["play_times"] = self.driver.find_element_by_xpath("//strong[@id='play-count']").text
            print(content_dict["play_times"])
            content_dict["author"] = self.driver.find_element_by_xpath("//span[@class='name']/a").text
            content_dict["released_time"] =self.driver.find_element_by_xpath("//span[@class='time s-fc4']").text
            content_dict["total_num"] = self.driver.find_element_by_xpath("//span[@id='playlist-track-count']").text
            tag_list = self.driver.find_elements_by_xpath("//div[@class='tags f-cb']/a/i")
            content_dict["tag"] = " ".join([i.text for i in tag_list])
            tr_list =self.driver.find_elements_by_xpath("//div[@id='song-list-pre-cache']//tbody/tr")
            print(len(tr_list))
            for tr in tr_list:
                content = dict()
                content["num"] = tr.find_element_by_xpath("./td[1]/div/span[2]").text
                content["title"] = tr.find_element_by_xpath("./td[2]//span[@class='txt']//b").get_attribute("title")
                content["singer"] = tr.find_element_by_xpath("./td[4]/div").get_attribute("title")
                content["Album"] =tr.find_element_by_xpath("./td[5]//a").get_attribute("title")
                content_list.append(content)
            content_dict["list"] = content_list
            print(content_dict)
            self.detail_queue.put(content_dict)
            self.play_dict_queue.task_done()

    def save(self):
        while True:
            content = self.detail_queue.get()
            list1 = content.pop("list") # 此时list1为歌曲信息字典列表，而content为歌单信息列表
            list2 = [{i[0]:i[1]} for i in content.items()]
            file_path = "spider_data/网易云.json"
            with open(file_path,"a",encoding="utf-8") as f:
                f.write(json.dumps(list2,ensure_ascii=False))
                f.write("\r\n")
                for i in list1:
                    f.write(json.dumps(i,ensure_ascii=False))
                    f.write("\r\n")
                print("保存成功:",content["title"])
            self.detail_queue.task_done()

    def main(self):
        # 准备start_url，webdriver
        # 获取请求，切换到包括内容的iframe
        thread_list = list()
        self.parse_url()
        for i in range(1):
            t1= Thread(target=self.get_detail)
            thread_list.append(t1)
        t2 = Thread(target=self.save)
        thread_list.append(t2)
        for t in thread_list:
            t.setDaemon(True)
            t.start()

        for q in [self.detail_queue,self.play_dict_queue]:
            q.join()
        print("over!!")

if __name__ == '__main__':
    music = WangYiYunSpider()
    music.main()