# coding = utf-8
import requests
from lxml import etree
import json

class QiuShiSpider(object):
    def __init__(self,type):
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        self.type = type
        self.start_url = "https://www.qiushibaike.com/"+type
        self.https_header = "https://www.qiushibaike.com"

    def send_url(self,url):
        # 发送请求，获取响应
        response =requests.get(url,headers=self.header)
        # 为方便Xpath提取，转为element
        html_str = response.content.decode()
        return etree.HTML(html_str)

    def get_content(self,element):
        """获取标题、链接地址、图片，并以列表的形势返回;返回下次请求的地址"""
        content_list = []
        # 分组获取包含所需内容的div列表
        div_list = element.xpath("//div[@id='content-left']/div")
        # 遍历，获取每个div内的用户名、头绪I昂内容，标题，链接，图片,xpath所取得结果均为列表
        for div in div_list:
            content_dict={}
            # 用户名
            username = div.xpath("./div[@class='author clearfix']/a[2]/@title")
            content_dict["Username"] = username[0] if len(username) >0 else None
            # 用户头像
            user_img = div.xpath(".//a[@rel='nofollow']/img/@src")
            content_dict['user_img'] = "https:"+user_img[0] if len(user_img)>0 else None
            # 用户年龄
            age = div.xpath("./div[@class='author clearfix']/div/text()")
            content_dict["age"] = age[0] if len(age) > 0 else None
            # 用户性别
            gender = div.xpath("./div[@class='author clearfix']/div/@class")
            content_dict["gender"] = [i.split(" ")[-1] for i in gender][0] if len(gender)>0 else None
            # 标题
            title = [i.replace("\n","" ) for i in div.xpath("./a/div/span/text()")]
            content_dict["title"] = title[0] if len(title)>0 else None
            # 好笑数
            stas_vote = div.xpath(".//span[@class='stats-vote']/i/text()")
            content_dict["好笑数"] = stas_vote[0] if len(stas_vote)>0 else None
            # 内容链接
            href = div.xpath("./a/@href") # 链接缺少https://www.qiushibaike.com
            content_dict['href'] = self.https_header+ href[0] if len(href)>0 else None
            # 内容图片链接
            img =div.xpath("./div[@class='thumb']/a/img/@src")
            content_dict["img"] = "https:" + img[0] if len(img) >0 else None
            # content_dict = {"title":title,"href":href,"img":img}
            content_list.append(content_dict)
        # 如果存在下一页，则下一页为下一页的a标签地址，否则为空
        next = element.xpath("//span[@class='next']/../@href") # 链接缺少https://www.qiushibaike.com
        next_url = self.https_header + next[0] if  len(next)>0 else None
        print(next_url)

        return content_list,next_url

    def save_content(self,content_list):
        # 在windows下面新文件的默认编码是gbk，所以想要向新文件里写数据需要改变新文件的编码：
        with open("糗事百科.json","a",encoding='utf-8') as f:
            # 只能写入字符串，因此需用json.dumps()转化,每行表示一个链接
            for content in content_list:
                print(content)
                # 将字典转为字符串，才能支持写入，为啥写入中文乱码，写入的是json？
                f.write(json.dumps(content,ensure_ascii=False))
                f.write("\n")
        print("糗事百科%s保存成功！"%self.type)

    def main(self):
        # 1. 起始页url
        # 2. 发送请求，获取响应
        next_url = self.start_url
        while next_url:
            element = self.send_url(next_url)
            # 3. 提取数据及下一页URL
            content_list,next_url = self.get_content(element)
            # 4. 保存数据
            self.save_content(content_list)

if __name__ == '__main__':
    qiushi = QiuShiSpider("pic")
    qiushi.main()