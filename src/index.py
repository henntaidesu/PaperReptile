from src.paper_website.arxiv.arxivorg import ArxivOrg, translate_classification, translate_title
from src.module.log import log
from src.module.multi_process import Process
from src.paper_website.arxiv.arxiv_paper_down import Arxiv_paper_down
from src.paper_website.cnki.run_cnki import run_get_paper_title, run_get_paper_info
import asyncio


class index:

    def __init__(self):
        self.logger = log()
        self.arxivorg = ArxivOrg()
        self.process = Process()
        self.Arxiv_paper_down = Arxiv_paper_down()

    def index(self):
        flag = '5'
        if flag == '1':
            print("爬arxiv论文")
            self.arxivorg.get_exhaustive_url()

        if flag == '2':
            print("翻译classification")
            while True:
                sql = f"SELECT UUID, classification_en FROM `index` WHERE state = '00'"
                asyncio.run(self.process.multi_process_as_up_group(sql, translate_classification))

        if flag == '3':
            print("翻译title")
            while True:
                sql = (f" SELECT UUID, title_en FROM `Paper`.`index`"
                       f" WHERE state = '01' and classification_zh  like '%cs%' "
                       f" ORDER BY receive_time desc limit 10000")
                self.process.multi_process_as_up_group(sql, translate_title)

        if flag == '4':
            print("下载arxiv论文")
            while True:
                sql = (f"SELECT UUIDs, web_site_id, version, withdrawn "
                       f"FROM `Paper`.`index`WHERE state = '02' and classification_zh "
                       f" like '%cs%' ORDER BY receive_time desc limit 10000")
                self.Arxiv_paper_down.paper_down(sql)

        if flag == '5':
            print("获取cnki论文基础数据")
            run_get_paper_title()

        if flag == '6':
            print("获取cnki论文详细数据")
            while True:
                sql = (f"SELECT * FROM `cnki_index` WHERE `start` = '0'  AND db_type > '0' "
                       f"ORDER BY receive_time DESC LIMIT 10000, 10000")
                self.process.multi_process_as_up_group(sql, run_get_paper_info)

            # run_get_paper_info()

