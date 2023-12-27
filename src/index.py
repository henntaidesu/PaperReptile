from src.paper_website.arxiv.arxivorg import ArxivOrg, translate_classification, translate_title
from src.module.log import log
from src.module.multi_process import Process
from src.paper_website.arxiv.arxiv_paper_down import Arxiv_paper_down
from src.paper_website.cnki.cnki import cnki_run
import asyncio


class index:

    def __init__(self):
        self.logger = log()
        self.arxivorg = ArxivOrg()
        self.process = Process()
        self.Arxiv_paper_down = Arxiv_paper_down()

    def index(self):
        print("1:爬论文")
        print("2:翻译classification")
        print("3:翻译title")
        # paper_units = input()
        # self.arxivorg.get_exhaustive_url(paper_units)

        # flag = input()
        flag = '5'
        if flag == '1':
            self.arxivorg.get_exhaustive_url()

        if flag == '2':
            while True:
                sql = f"SELECT UUID, classification_en FROM `index` WHERE state = '00'"
                asyncio.run(self.process.multi_process_as_up_group(sql, translate_classification))

        if flag == '3':
            while True:
                sql = (f" SELECT UUID, title_en FROM `Paper`.`index`"
                       f" WHERE state = '01' and classification_zh  like '%cs%' "
                       f" ORDER BY receive_time desc limit 10000")
                self.process.multi_process_as_up_group(sql, translate_title)

        if flag == '4':
            while True:
                sql = (f"SELECT UUID, web_site_id, version, withdrawn "
                       f"FROM `Paper`.`index`WHERE state = '02' and classification_zh "
                       f" like '%cs%' ORDER BY receive_time desc limit 10000")
                self.Arxiv_paper_down.paper_down(sql)

        if flag == '5':
            keyword = "人工智能"
            papers_need = 2147483647
            cnki_run(keyword, papers_need)
