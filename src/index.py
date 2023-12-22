from src.paper_website.arxiv.arxivorg import ArxivOrg, translate_classification, translate_title
from src.module.log import log
from src.module.multi_process import Process
from src.paper_website.arxiv.arxiv_paper_down import Arxiv_paper_down
import asyncio


class index:

    def __init__(self):
        self.logger = log()
        self.arxivorg = ArxivOrg()
        self.process = Process()
        self.Arxiv_paper_down = Arxiv_paper_down()

    def index(self):
        try:
            print("1:爬论文")
            print("2:翻译classification")
            print("3:翻译title")
            # paper_units = input()
            # self.arxivorg.get_exhaustive_url(paper_units)

            # flag = input()
            flag = '4'
            if flag == '1':
                self.arxivorg.get_exhaustive_url()

            if flag == '2':
                while True:
                    sql = f"SELECT UUID, classification_en FROM `index` WHERE state = '00'"
                    asyncio.run(self.process.multi_process_as_up_group(sql, translate_classification))

            if flag == '3':
                while True:
                    sql = (f"SELECT UUID, title_en FROM `Paper`.`index`WHERE state = '01' "
                           f"and classification_zh not like '%cs%' ORDER BY receive_time desc limit 1000")
                    self.process.multi_process_as_up_group(sql, translate_title)

            if flag == '4':
                while True:
                    sql = (f"SELECT UUID, web_site_id, version, withdrawn "
                           f"FROM `Paper`.`index`WHERE state = '02' and classification_zh "
                           f"like '%cs%' ORDER BY receive_time desc limit 1000")
                    self.Arxiv_paper_down.paper_down(sql)
        except:
            self.index()
