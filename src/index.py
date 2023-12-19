from src.paper_website.arxivorg import ArxivOrg, translate_classification, translate_title
from src.module.log import log
from src.module.multi_process import Process

import sys


class index:

    def __init__(self):
        self.logger = log()
        self.arxivorg = ArxivOrg()
        self.process = Process()

    def index(self):
        print("1:爬论文")
        print("2:翻译classification")
        print("3:翻译title")
        # paper_units = input()
        # self.arxivorg.get_exhaustive_url(paper_units)

        # flag = input()
        flag = '1'
        if flag == '1':
            self.arxivorg.get_exhaustive_url()

        if flag == '2':
            while True:
                sql = f"SELECT UUID, classification_en FROM `index` WHERE state = '00'"
                self.process.multi_process_as_up_group(sql, translate_classification)

        if flag == '3':
            while True:
                sql = f"SELECT UUID, title_en  FROM `index` WHERE state = '01'"
                self.process.multi_process_as_up_group(sql, translate_title)
