import requests
from bs4 import BeautifulSoup
import os
import re
import time

# 得到书籍信息的类GetBookInfo，比如页面链接、起始页面、终止页面、书名
class GetBookInfo(object):
    def __init__(self, root_url):
        self.root_url = root_url
        pass
    
    def get_book_info(self):
        # 设置头部参数
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        }
        response = requests.get(self.root_url, headers=headers)
        response.encoding = 'utf-8' # 设置字符编码（中文极有可能乱码，因此设置utf-8编码较为妥当）
        soup = BeautifulSoup(response.text, 'lxml')

        # book_file = open('jyBookInfo' + '.txt', 'w', newline='', encoding='utf-8')
        book_info = soup.find('dl', class_='cat_box').find_all('dd')
        # print(book_info)
        for x in book_info:
            book_url = x.find('a').get('href')
            book_name = x.find('b').get_text()
            # print(book_url,book_name)

            # 调用另外一个函数获取书籍的起始页面url和结束页面的url
            bookNav.get_book_id(book_url, book_name)
        pass

    def get_book_id(self, book_url, book_name):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        }
        page_url = 'http://jinyongxiaoshuo.com' + book_url
        response = requests.get(page_url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        tmp = soup.find('dl', class_='cat_box').find_all('dd')[0].find('a').get('href')

        # start_id、end_id分别是对应每本书的起始页面和结束页面的数字
        start_id = int(re.findall(r'\d+', tmp)[0])
        tmp = soup.find('dl', class_='cat_box').find_all('dd')[-1].find('a').get('href')
        end_id = int(re.findall(r'\d+', tmp)[0])
        # print(start_id, end_id)

        # 写入文本文件中
        book_file = open('jyBookInfo' + '.txt', 'a', newline='', encoding='utf-8')
        print('{} {} {} {}'.format(book_url, start_id, end_id, book_name), file=book_file)
        book_file.close()
        pass

# 得到金庸全集小说内容的类JyFiction
class JyFiction(object):
    def __init__(self, page_url):
        self.page_url = page_url
        pass

    def get_fiction(self, book_url, start, end, book_name):

        # 便于管理，每本书当创建一个目录
        if not os.path.exists('{}'.format(book_name)):
            os.mkdir('{}'.format(book_name))

        page_url = self.page_url + book_url
        # 大部分书的id都是逐步减一递减的，因此步长step设置为-1
        step = -1
        # 某些书只有一个章节，因此要特殊考虑一下
        if start == end:
            step = 1
        for id_page in range(start, end + 1, step):
            try:
                real_url = page_url + str(id_page) + '.html'
                # print(real_url)
                self.get_text_content(book_name, real_url)
            except:
                pass
        pass

    def get_text_content(self, dir_name, real_url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        }
        response = requests.get(real_url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('div', id='post-472').find('h1')  # 每个章节名称，并设置为对应的章节名称，如 第一回 危邦行蜀道 乱世坏长城.txt
        # print(title.text)

        txt_file = open('./{}/'.format(dir_name) + title.text +
                        '.txt', 'w', newline='', encoding='utf-8')
        print('{}\n'.format(title.text), file=txt_file)

        # 便于查看获取的进度，特意打印每本书的每个章节的标题
        print('{}\n'.format(title.text))
        # 获取每本书的内容，并保存到本地的文本文件中
        content = soup.find('div', class_='entry').find_all('p')
        for p in content:
            print('{}\n'.format(p.text), file=txt_file)
        txt_file.close()

if __name__ == '__main__':

    # 下面三行得到jyBookInfo.txt文件，其中保存了书籍的link、start_id、end_id、book_name（使用之后需要注释这三行，并手动删除.txt的最后一个空行）
    # root_url = 'http://jinyongxiaoshuo.com/xinxiu/'
    # bookNav = GetBookInfo(root_url)
    # bookNav.get_book_info()

    # 读取jyBookInfo.txt文件，通过爬虫进一步解析每本书的具体章节内容
    url = 'http://jinyongxiaoshuo.com'
    jy = JyFiction(url)
    with open('./jyBookInfo.txt', 'r', encoding='utf-8') as f:
        item = f.readline()
        while item:
            book_url, start, end, book_name = map(str, item.split())
            # print(book_url, start, end, book_name)
            jy.get_fiction(book_url, int(start), int(end), book_name)
            # time.sleep(2)
            item = f.readline()