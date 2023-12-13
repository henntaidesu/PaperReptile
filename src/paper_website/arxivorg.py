import sys
from datetime import datetime
import requests
import re
import time
from lxml import html
from src.module.read_conf import read_conf, ArxivYYMM
from bs4 import BeautifulSoup
from src.model.arxiv_org import PageUrl
from src.module.execution_db import db
from src.module.now_time import now_time
from src.module.UUID import UUID
from src.module.log import log
from src.module.translate import translate
from src.module.chatGPT import openAI


class ArxivOrg:

    def __init__(self):
        self.session = requests.Session()
        self.conf = read_conf()
        self.if_proxy, self.proxies = self.conf.proxy()
        if self.if_proxy is True:
            self.session.proxies.update(self.proxies)
        self.url_list = PageUrl()
        self.logger = log()
        self.date_base = db()
        self.tr = translate()
        self.GPT = openAI()

    def read_yy_mm(self):
        conf = ArxivYYMM()
        yy_mm, code = conf.read_arxiv_yy_mm_code()
        code = str(int(code) + 1).zfill(5)

        return yy_mm, code

    def write_code(self, yy_mm, code):
        conf = ArxivYYMM()
        conf.write_arxiv_yy_mm_code(yy_mm, code)

    def write_yy_mm_code(self, yy_mm):
        conf = ArxivYYMM()
        yy, mm = divmod(int(str(yy_mm)) - 1, 100)
        if mm == 0:
            yy, mm = yy - 1, 12
            self.logger.write_log(f"本年度已爬取{yy}")
            sys.exit()
            yy, mm = 99, 12
        conf.write_arxiv_yy_mm_code(f"{yy:02d}{mm:02d}", "00000")

    def TrimString(self, Str):
        # if '\n' in Str:
        #     Str = Str.replace('\n', ' ')
        # if ' ' in Str:
        #     Str = Str.replace(' ', '')
        # if '/' in Str:
        #     Str = Str.replace('/', ' ')
        if "'" in Str:
            Str = Str.replace("'", "\\'")
        if '"' in Str:
            Str = Str.replace('"', '\\"')
        return Str

    def TrSQL(self, sql):
        sql = sql.replace("None", "NULL").replace("'NULL'", "NULL")
        return sql

    def get_exhaustive_url(self):
        while True:
            uuid = None
            yy_mm = None
            code = None
            classification_en = None
            classification_zh = None
            title_zh = None
            title_en = None
            Now_time = None
            authors_list = None
            introduction = None
            receive_time = None
            Journal_reference = None
            Comments = None
            size = None
            DOI = None
            version = None
            withdrawn = None

            yy_mm, code = self.read_yy_mm()
            url = f"https://arxiv.org/abs/{yy_mm}.{code}"
            self.logger.write_log(url)
            try:
                response = self.session.get(url)
            except Exception as e:
                if type(e).__name__ == 'SSLError':
                    self.logger.write_log("SSL Error")
                    time.sleep(3)
                    self.get_exhaustive_url()
                self.logger.write_log(f"Err Message:,{str(e)}")
                self.logger.write_log(f"Err Type:, {type(e).__name__}")
                _, _, tb = sys.exc_info()
                self.logger.write_log(
                    f"Err Local:, {tb.tb_frame.f_code.co_filename}, {tb.tb_lineno}")

            tree = html.fromstring(response.content)
            soup = BeautifulSoup(response.text, 'html.parser')

            data_flag = tree.xpath('/html/head/title')[0].text if tree.xpath('/html/head/title') else None
            if "Article not found" in data_flag:
                self.logger.write_log(f"   已爬取完{yy_mm}数据   ")
                self.write_yy_mm_code(yy_mm)
                self.get_exhaustive_url()

            title_en = str(tree.xpath('//*[@id="abs"]/h1/text()')[0])[2:-2]
            time.sleep(1)
            # title_zh = self.tr.GoogleTR(title, 'zh-CN')
            # title_zh = self.tr.baiduTR("en", "zh", title)
            title_en = self.TrimString(title_en)

            authors_list = " , ".join([p.get_text() for p in soup.find('div', class_='authors').find_all('a')])
            authors_list = self.TrimString(authors_list)
            if len(authors_list) > 512:
                authors_list = authors_list[:512]

            introduction = " , ".join(tree.xpath('//*[@id="abs"]/blockquote/text()')[1:])
            introduction = self.TrimString(introduction)

            classification = str(soup.find('td', class_='tablecell subjects').get_text(strip=True))
            time.sleep(1)
            # classification_zh = self.tr.GoogleTR(classification, 'zh-CN')
            # classification_zh = self.tr.baiduTR("en", "zh", classification)

            classification_en = self.TrimString(classification)

            Journal_reference = soup.find('td', class_='tablecell jref')
            if Journal_reference:
                Journal_reference = Journal_reference.text
                Journal_reference = self.TrimString(Journal_reference)

            Comments = soup.find('td', class_='tablecell comments mathjax')
            if Comments:
                Comments = Comments.text
                Comments = self.TrimString(Comments)

            receive_time = soup.find('div', class_='submission-history')
            receive_time = receive_time.get_text(strip=True)

            size = receive_time[receive_time.rfind("(") + 1:][:-4]
            withdrawn = "0"
            if size == "withdr":
                withdrawn = "1"
                size = receive_time[:receive_time.rfind("[")][:-4]
                size = size[size.rfind("(") + 1:]
            if ',' in size:
                size = size.replace(",", "")

            DOI = (soup.find('td', class_='tablecell arxivdoi')).find('a')['href'][16:]

            if "[v4]" in receive_time:
                receive_time = receive_time[receive_time.find("[v2]") + 9:]
                receive_time = datetime.strptime(receive_time[:receive_time.find("UTC") - 1], "%d %b %Y %H:%M:%S")
                version = '4'

            elif "[v3]" in receive_time:
                receive_time = receive_time[receive_time.find("[v3]") + 9:]
                receive_time = datetime.strptime(receive_time[:receive_time.find("UTC") - 1], "%d %b %Y %H:%M:%S")
                version = '3'

            elif "[v2]" in receive_time:
                receive_time = receive_time[receive_time.find("[v2]") + 9:]
                receive_time = datetime.strptime(receive_time[:receive_time.find("UTC") - 1], "%d %b %Y %H:%M:%S")
                version = '2'

            else:
                receive_time = receive_time[receive_time.find("[v1]") + 9:]
                receive_time = datetime.strptime(receive_time[:receive_time.find("UTC") - 1], "%d %b %Y %H:%M:%S")
                version = '1'

            Now_time, uuid = now_time(), UUID()

            sql = (f"INSERT INTO `index`"
                   f"(`UUID`, `web_site_id`, `classification_en`, `classification_zh`, `source_language`, "
                   f"`title_zh`, `title_en`, `update_time`, `insert_time`, `from`, `state`, `authors`, `Introduction`, "
                   f"`receive_time`, `Journal_reference`, `Comments`, `size`, `DOI`, `version`, `withdrawn`)"
                   f" VALUES ('{uuid}', '{yy_mm}.{code}', '{classification_en}', '{classification_zh}', 'en', "
                   f"'{title_zh}', '{title_en}', NULL, '{Now_time}', 'arxiv', '00', '{authors_list}', '{introduction}',"
                   f"'{receive_time}','{Journal_reference}','{Comments}',{size},'{DOI}','{version}','{withdrawn}');")

            sql = self.TrSQL(sql)
            date_base = db()
            date_base.insert_all(sql)
            self.write_code(yy_mm, code)
            # print("sleep 2s")
            # time.sleep(2)

    def translate_classification_title(self):
        try:
            classification_en = None
            title_en = None
            sql = f"SELECT UUID, classification_en,  title_en  FROM `index` WHERE state = '00' limit 100"
            date_base = db()
            flag, data = date_base.select_all(sql)
            # print(data)
            for i in data:
                uuid = None
                classification_en = None
                classification_cn = None
                title_en = None
                title_cn = None
                Now_time = None
                Now_time = now_time()
                uuid = i[0]
                classification_en = i[1]
                title_en = i[2]

                # classification_cn = self.GPT.openai_chat(classification_cn)
                classification_cn = self.tr.GoogleTR(classification_en, 'zh-CN')
                # classification_cn = self.tr.baiduTR("en", "zh", classification_en)

                title_cn = self.GPT.openai_chat(title_en)
                # title_cn = self.tr.GoogleTR(title_cn, 'zh-CN')
                # title_cn = self.tr.baiduTR("en", "zh", title_cn)

                classification_cn = self.TrimString(classification_cn)
                title_cn = self.TrimString(title_cn)

                self.logger.write_log(f"[EN : {classification_en}] -> [CN : {classification_cn}]")
                self.logger.write_log(f"[EN : {title_en}] -> [CN : {title_cn}]")
                sql = (f"UPDATE `index` SET `classification_zh` = '{classification_cn}',`title_zh` = '{title_cn}' "
                       f" , `state` = '01', `update_time` = '{Now_time}' WHERE `UUID` = '{uuid}';")
                date_base = db()
                date_base.update_all(sql)


        except Exception as e:
            if type(e).__name__ == 'SSLError':
                self.logger.write_log("SSL Error")
                time.sleep(3)
                self.translate_classification_title()
            self.logger.write_log(f"Err Message:,{str(e)}")
            self.logger.write_log(f"Err Type:, {type(e).__name__}")
            _, _, tb = sys.exc_info()
            self.logger.write_log(
                f"Err Local:, {tb.tb_frame.f_code.co_filename}, {tb.tb_lineno}")
