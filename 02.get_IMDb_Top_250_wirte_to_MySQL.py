import requests
import pymysql
import sys
from bs4 import BeautifulSoup

class MovieSpider(object):
    def __init__(self, page_url):
        self.page_url = page_url
        pass

    def get_all_movie(self):
        html = requests.get(self.page_url)
        soup = BeautifulSoup(html.text, "html.parser")
        soup.encode("utf-8")

        bar = ProgressBar(250, 50)
        movie_ls, rank = [], 1
        items = soup.find("div", class_ = "article").find("tbody", class_ = "lister-list").find_all("tr")
        for i in items:
            movie_info = {}
            # print(i.find("td", class_ = "titleColumn").find("a").string)
            bar.show_progress_bar(rank)
            movie_info["MovieRanking"] = str(rank)
            movie_info["MovieName"] = i.find("td", class_ = "titleColumn").find("a").string
            movie_info["Years"] = i.find("td", class_ = "titleColumn").find("span").string[1:-1]
            movie_info["Score"] = i.find("td", class_ = "ratingColumn imdbRating").find("strong").string
            movie_ls.append(movie_info)
            rank += 1
        bar.close(1)
        return movie_ls
        pass

    def save_to_MySQL(self, ls):
        # 连接数据库并创建游标cursor
        db = pymysql.connect(host='192.168.56.3', port=3306, user='root', password='123456', charset='utf8')
        cursor = db.cursor()
        cursor.execute("DROP DATABASE IF EXISTS dbmovie")
        cursor.execute("CREATE DATABASE dbmovie")
        cursor.execute("USE dbmovie")
        cursor.execute("DROP TABLE IF EXISTS IMDbTOP250")
        creat_table = "CREATE TABLE `IMDbTOP250` (`rank` VARCHAR(4), `title` VARCHAR(70), `years` VARCHAR(4), `score` VARCHAR(4))"
        cursor.execute(creat_table)

        # 写入到 MySQL中
        bar = ProgressBar(250, 50)
        i = 1
        for item in ls:
            insert_sql = "INSERT INTO `IMDbTOP250` (`rank`, `title`, `years`, `score`) VALUE (%s, %s, %s, %s)"
            # insert_sql = "INSERT INTO `IMDbTOP250` (`Rank`, `Title`, `CNtitle`, `Years`) VALUE (%s, %s, %s, %s)"
            # try:
            cursor.execute(insert_sql, [item["MovieRanking"], item["MovieName"], item["Years"], item["Score"]])
            bar.show_progress_bar(i)
            i += 1
            # print(item["MovieName"] + ' -->insert into successful...')
            db.commit() #提交到数据库
            # except:
            #     db.rollback()
        bar.close(0)
        # 关闭游标及数据库
        cursor.close()
        db.close()
        pass

    # def save_as_text():
    #     with open("./IMDb Top 250.txt", "w", encoding = "utf-8") as file:
    #         for x in ls:
    #             file.write(x["MovieRanking"] + "\t" + x["MovieName"] + "\t" + x["Years"] + "\n")
    #     pass

class ProgressBar(object):
    def __init__(self, max_step, max_arrow):
        self.max_step = max_step
        self.max_arrow = max_arrow
        pass

    def show_progress_bar(self, i):
        cnt_arrow = int(i * self.max_arrow / self.max_step) # ">"表示已经处理过
        cnt_line = self.max_arrow - cnt_arrow # "-"未处理过
        percent = i * 100 / self.max_step
        process_bar = '\r' +'[' + '>' * cnt_arrow + '-' * cnt_line +']' + '%.2f' % percent + '%' #带输出的字符串，'\r'表示不换行回到最左边  
        sys.stdout.write(process_bar) #这两句打印字符到终端
        sys.stdout.flush()
        pass

    def close(self, flag = 0):
        print("", "电影抓取完成:)") if flag == 1 else print("", "写入数据库成功～")
        pass

if __name__ == "__main__":
    page_url = "https://www.imdb.com/chart/top?ref_=nv_mv_250"
    top = MovieSpider(page_url)
    all_movies = top.get_all_movie()
    # for x in all_movies:
    #    print(x)
    top.save_to_MySQL(all_movies)