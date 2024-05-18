import time
import requests
from tqdm import tqdm
from src.module.execution_db import DB
from src.module.log import Log
from src.module.read_conf import ReadConf
from src.module.now_time import now_time
from src.module.rabbitMQ import rabbitmq_produce

import os


class Arxiv_paper_down:

    def __init__(self):
        self.conf = ReadConf()
        self.session = requests.Session()
        self.if_proxy, self.proxies = self.conf.http_proxy()
        if self.if_proxy is True:
            self.session.proxies.update(self.proxies)
        self.down_path = self.conf.down_path()
        self.logger = Log()

    def paper_down(self, sql):
        flag, data = DB().select(sql)
        url = None
        for i in data:
            uuid = i[0]
            file_name = i[1]
            version = int(i[2])
            withdrawn = int(i[3])
            if withdrawn == 1:
                continue
            for ver in range(1, version + 1):
                paper_version = None
                if '.' in file_name:
                    paper_version = f"{file_name}v{ver}"
                    url = f"https://arxiv.org/pdf/{paper_version}.pdf"
                if '/' in file_name:
                    continue
                print(f"{paper_version} - {url}")
                year = str(file_name)[:2]
                moon = str(file_name)[2:][:2]
                # num = int(str(file_name)[4:])

                file_path = f"{self.down_path}/arxiv/{year}/{moon}"
                os.makedirs(file_path, exist_ok=True)

                file_path = os.path.join(file_path, f"{paper_version}.pdf")

                try:
                    response = self.session.get(url)

                    if os.path.exists(file_path):  # 如果文件已存在，获取已下载的文件大小
                        resume_header = {'Range': 'bytes=%d-' % os.path.getsize(file_path)}
                        response = self.session.get(url, headers=resume_header)
                    else:
                        response = self.session.get(url)

                    download_complete = False
                    while not download_complete:
                        try:
                            if response.status_code == 200 or response.status_code == 206:  # 206表示部分内容
                                total_size = int(response.headers.get('content-length', 0))
                                block_size = 1024
                                progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)

                                with open(file_path, 'ab') as file:  # 使用追加模式打开文件
                                    for data in response.iter_content(block_size):
                                        progress_bar.update(len(data))
                                        file.write(data)

                                progress_bar.close()
                                Time = now_time()
                                sql = f"UPDATE `index` SET  `state` = '03' ,`update_time` = '{Time}' WHERE " \
                                      f"`uuid` = '{uuid}';"
                                rabbitmq_produce('MYSQL_UPDATE', sql)

                                download_complete = True  # 下载完成

                            else:
                                self.logger.write_log(f"{response.status_code}", 'error')

                                time.sleep(3)

                        except requests.exceptions.RequestException as e:
                            print(f"网络错误: {e}")
                            time.sleep(3)
                            self.paper_down(sql)
                except Exception as e:
                    self.logger.write_log(f"{e}", 'error')
                    self.paper_down(sql)
