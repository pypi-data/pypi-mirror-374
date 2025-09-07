TEMPLATE_LIST = [
    {
        "keyword":"模板爬虫",
        "code_block": '''import requests
import bs4
import time
head = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11"
}# 设置请求头，模拟浏览器
#TODO 修改下方需要爬取的网址
url = "https://static0.xesimg.com/pythonweb/dogs.html"
# 请求网页
res = requests.get(url, headers=head)
res.encoding = res.apparent_encoding  # 设置编码格式
# print(res)  # 查看状态码
# print(res.text)  # 查看网页HTML代码
soup = bs4.BeautifulSoup(res.text, "lxml")  # 解析网页
# 选取数据
#TODO 修改下方爬取条件中的标签名、属性
tags = soup.find_all("div", class_="tit")

# 展示结果
for t in tags:
    print(t.text)
    
    #TODO 取消下面代码的注释，可以保存内容到txt中
    # with open("内容.txt", "a", encoding="UTF-8") as file:
    # #TODO 修改要写入的内容
    #     file.write(t.text + "\n")
'''
    }
    
]
