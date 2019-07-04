import requests
import json

class Translate(object):
    def __init__(self,data):
        self.detect_url = "https://fanyi.baidu.com/langdetect"
        # self.header = {"User_Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) "
        #                             "AppleWebKit/537.36 (KHTML, like Gecko) "
        #                             "Chrome/72.0.3626.121 Safari/537.36"}
        # self.trs_url = "https://fanyi.baidu.com/v2transapi"
        self.header = {"User_Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/72.0.3626.121 Mobile Safari/537.36"}
        self.trs_url = "https://fanyi.baidu.com/basetrans"
        self.data = data

    def url_post(self,url,kw):
        response = requests.post(url,headers=self.header,data=kw)
        html_str = response.content.decode("utf-8")
        return html_str

    def langdetect(self,query):
        dict = self.url_post(self.detect_url,query) # json
        # print(dict)
        dict = json.loads(dict)
        return dict["lan"]

    def translate(self,data):
        result = self.url_post(self.trs_url,data)
        print(type(result))
        result = json.loads(result)  # 无法解析？不是json？？？
        print(result)
        # return result["trans"][0]["dst"]

    def run(self):
        # 1. 判断目标语言,确定翻译语言
        lan = self.langdetect({"query" :self.data})
        # 2.发送请求
        trs_data = {"from": "zh", "to": "en","query":self.data} if lan=="zh" else\
            {"from": "en", "to": "zh","query":self.data} # 扁平胜于嵌套
        ret = self.translate(trs_data)
        print("翻译结果：%s"%ret)

if __name__ == '__main__':
    fanyi = Translate("hello")
    fanyi.run()

