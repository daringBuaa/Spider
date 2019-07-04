import requests

# 贴吧爬虫
class TieBaSpider(object):
    def __init__(self,tiebaname):
        self.name = tiebaname
        self.url = "https://tieba.baidu.com/f?ie=utf-8&kw="+tiebaname+"&ie=utf-8&pn={}"
        self.headers = {'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36'}
        self.cookies = 'BAIDUID=3C204798CAE5A9AF1EC06F92865F97EF:FG=1; BIDUPSID=3C204798CAE5A9AF1EC06F92865F97EF; PSTM=1544700996; TIEBA_USERTYPE=251e382d596d9a218f036cd5; TIEBAUID=e23d39f366bd30bb62d3e80f; bdshare_firstime=1546419988393; MCITY=-81%3A; NO_UNAME=1; BDUSS=-; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; H_PS_PSSID=1433_28795_21078_28769_28724_28557_28833_28584_26350_28604_28626_28606; PSINO=1; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1552698371,1553239444,1553846295,1555051124; Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948=1555051138'


    def get_urls(self):
        # url_list = []
        # for i in range(10):
        #     url_list.append(self.url.format(50*i))
        # return  url_list
        # 可用列表生成式简化
        # python之禅 ： 扁平胜于嵌套
        return [ self.url.format(50*i) for i in range(1000)]

    def get_response(self,url):
        # 使用字典生成公式让字符串转化成字典
        cookies = {i.split("=")[0]:i.split("=")[1] for i in self.cookies.split(";")}
        # 加入cookie 避免被识别爬虫
        response = requests.get(url, headers=self.headers,cookies=cookies) # get方法中参数均为字典
        content = response.content.decode()
        return content

    def file_save(self,content,page):
        # 文件名应包括路径和后缀，若不写路径则默认当前文件夹！但文件必须有后缀
        filename = str(self.name + "吧第{}页.html").format(page) # 字符串格式化输出format
        # 遇到写入bug 加上encoding方式
        with open(filename,"w",encoding='utf-8') as f:
            f.write(content)

    def run(self):
        # 获取url https://tieba.baidu.com/f?ie=utf-8&kw=李毅&ie=utf-8&pn=0
        # 主程序只负责逻辑，具体运行由其他方法执行，主程序只负责调用
        url_list = self.get_urls()
        for url in url_list:
            # 发送请求获取响应,提取内容
            content = self.get_response(url)
            # 保存文件
            page = url_list.index(url) + 1
            self.file_save(content,page)
            print("\r%s吧第%d页spider成功"%(self.name,page),end="")

if __name__ == '__main__':
    name = input("请输入你想spider的贴吧名：")
    # liyi = TieBaSpider("李毅")
    # liyi.run()
    lol = TieBaSpider(name)
    lol.run()

