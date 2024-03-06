import sys
import requests
from elasticsearch import Elasticsearch
from src.module.log import Log, err1
from src.module.execution_db import Date_base
from src.module.read_conf import read_conf
from src.module.now_time import now_time
from datetime import datetime
import json


def create_arxiv_index(data):
    ES_URL = f'http://{read_conf().elasticsearch()}:9200'
    UUID = None
    try:
        for paper_index in data:
            UUID = paper_index[0]
            WEB_SIDE_ID = paper_index[1]
            classification_en = paper_index[2]
            classification_zh = paper_index[3]
            source_language = paper_index[4]
            title_zh = paper_index[5]
            title_en = paper_index[6]
            paper_from = paper_index[9]
            authors = paper_index[11]
            Introduction = paper_index[12]
            receive_time = paper_index[13]
            Journal_reference = paper_index[14]
            Comments = paper_index[15]
            size = paper_index[16]
            DOI = paper_index[17]
            receive_time = f"{int(receive_time.timestamp())}000"

            # 处理空值
            classification_zh = classification_zh or ""
            authors = authors or ""

            # 拆分字段
            classification_zh_list = classification_zh.split('；')
            authors_list = authors.split(',')

            # 写入主索引
            arxiv_index_body = {
                "UUID": UUID,
                "WEB_SIDE_ID": WEB_SIDE_ID,
                "source_language": source_language,
                "title_zh": title_zh,
                "title_en": title_en,
                "paper_from": paper_from,
                "Introduction": Introduction,
                "receive_time": receive_time,
                "Journal_reference": Journal_reference,
                "Comments": Comments,
                "size": size,
                "DOI": DOI
            }
            # arxiv_index_body = str(arxiv_index_body).replace("'", '"')
            # print(arxiv_index_body)

            response = requests.post(f"ES_URL/_doc/{UUID}", data=arxiv_index_body)

            response = response.json()
            print(response)

            sys.exit()


            # 写入分类索引
            for classification in classification_zh_list:
                arxiv_paper_classification_zh_body = {
                    "UUID": UUID,
                    "classification_zh": classification.strip()  # 去除空格
                }
                es.index(index="arxiv_classification_zh", body=arxiv_paper_classification_zh_body)

            # 写入作者索引
            for author in authors_list:
                arxiv_paper_authors_body = {
                    "UUID": UUID,
                    "authors": author.strip()  # 去除空格
                }
                es.index(index="arxiv_authors", body=arxiv_paper_authors_body)

            # 更新 SQL
            sql = f"UPDATE `Paper`.`index` SET `ES_date` = '{now_time()}' WHERE `UUID` = '{UUID}';"
            Date_base().update_all(sql)

            Log().write_log(f'写入Es成功 {title_zh}', 'info')

    except Exception as e:
        Log().write_log(f'写入Es失败 {UUID}', 'error')
        err1(e)

