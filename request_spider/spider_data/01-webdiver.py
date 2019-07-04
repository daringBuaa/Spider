# from selenium import webdriver
# import time
# """
# Chromedriver与Chrome的版本号必须一致
# """
#
# driver = webdriver.Chrome()
# driver.get("https://www.baidu.com")
# time.sleep(3)
# driver.quit()

import requests
url ="https://movie.douban.com/j/new_search_subjects?sort=U&range=0," \
                  "10&tags=%E7%94%B5%E8%A7%86%E5%89%A7&start=" \
                  "{}&countries=%E4%B8%AD%E5%9B%BD%E5%A4%A7%E9%99%86&year_range=2019,2019"
url = url.format(0)
print(url)# 可以取出url地址
headers = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
response = requests.get(url,headers=headers)