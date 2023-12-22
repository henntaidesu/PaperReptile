import requests
from src.module.execution_db import Date_base
from src.module.log import log
from src.module.read_conf import read_conf


class Arxiv_paper_down:

    def __init__(self):
        self.conf = read_conf()
        self.DB = Date_base()
        self.session = requests.Session()
        self.if_proxy, self.proxies = self.conf.http_proxy()
        if self.if_proxy is True:
            self.session.proxies.update(self.proxies)

    def paper_down(self, sql):
        flag, data = self.DB.select_all(sql)
        for i in data:
            if '.' in i[1]:
                url = f"https://arxiv.org/pdf/{i[1]}.pdf"
            if '/' in i[1]:
                url = f"https://arxiv.org/pdf/{i[1]}.pdf"
