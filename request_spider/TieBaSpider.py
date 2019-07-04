import requests
from lxml import etree
import json

class TieBaSpider(object):
    def __init__(self,tieba_name):
        self.name = tieba_name
        self.start_url = "https://tieba.baidu.com/f?kw="+tieba_name+"&ie=utf-8&pn={}"
        self.headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"}

    def send_url(self,url):
        response = requests.get(url,headers=self.headers)
        return response.content.decode()

    def get_info(self,html_str):
        """返回内容字典，以及下一次的url地址"""
        element = etree.HTML(html_str)
        # 1. 分组
        li_list = element.xpath("//div[@id='tlist']/ul/li[@data-tasktype]")
        # 2. 遍历
        content_list =[]
        for li in li_list:
            username = li.xpath("./div/div[2]/div/span/text()")[0]  # 取用户名
            head  = li.xpath("./div[1]/div[1]/img/@src")[0] # 取用户头像
            title = li.xpath("./a/div/span/text()")[0] # 取帖子标题
            detail = "https://tieba.baidu.com" +li.xpath("./a/@href")[0] # 取详情页url
            # print(detail)
            # 3.获取详情页信息
            content_detail_list = self.detail_content(detail,[])
            content_dict = {"uername":username,"userHead":head,"title":title,
                            "detail":content_detail_list}
            content_list.append(content_dict)
        return content_list

    def detail_content(self,url,content_list):
        print(url)
        response = self.send_url(url) # 封装的作用
        html_str = etree.HTML(response)
        img_list = html_str.xpath("//img[@class='BDE_Image']/@src") #//div[@class='content']
        print(img_list) ## 为什么取不出来，明明在网页上取出来了！！
        content_list.extend(img_list)
        next_url_list = html_str.xpath("//a[text()='下一页']/@href")
        print(len(next_url_list))
        if len(next_url_list)>0:
            next_url = next_url_list[0]

            return self.detail_content(next_url,content_list)
        return content_list


    def save(self,content,page):
        file_path =  self.name+ ".html"
        with open(file_path,"a",encoding="utf-8") as f:
            f.write(json.dumps(content,ensure_ascii=False,indent=2))
            f.write("\r\n")
        print("%s的%d页保存成功"%(self.name,page+1))

    def main(self):
        # 1.设置起始url
        i = 10 # 设置page
        url = self.start_url.format(i * 50)
        # 2.发送请求
        html_str = self.send_url(url)
        # 3.提取数据，下次url
        content = self.get_info(html_str)
        # 4.保存数据
        self.save(content,i)

if __name__ == '__main__':
    tieba = TieBaSpider('lol')
    tieba.main()


