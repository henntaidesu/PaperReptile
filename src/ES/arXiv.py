import sys
import time

import requests
from src.module.log import Log, err1
from src.module.execution_db import Date_base
from src.module.read_conf import ReadConf
from src.module.now_time import now_time
from datetime import datetime, timezone, timedelta
from src.model.ES import ArxivModel

model = ArxivModel()


def create_arxiv_index(data):
    ES_URL = ReadConf().elasticsearch()
    UUID = None
    dictionary = model.ES_classification()
    try:
        for paper_index in data:
            UUID = paper_index[0]
            WEB_SIDE_ID = paper_index[1]
            # classification_en = paper_index[2]
            classification_zh = paper_index[3]
            source_language = paper_index[4]
            title_zh = paper_index[5]
            title_en = paper_index[6]
            paper_from = paper_index[9]
            authors = paper_index[11]
            Introduction = paper_index[12]
            receive_time = str(paper_index[13])
            Journal_reference = paper_index[14]
            Comments = paper_index[15]
            size = paper_index[16]
            DOI = paper_index[17]

            # 时间戳转化
            receive_time = datetime.strptime(receive_time, "%Y-%m-%d %H:%M:%S")
            utc_offset = timedelta(hours=8)
            receive_time = receive_time.replace(tzinfo=timezone.utc) + utc_offset
            # 将datetime对象转换为ISO 8601字符串
            receive_time = receive_time.isoformat()

            # 拆分字段
            classification_zh_list = str(classification_zh).replace(';', '；').split('；')
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

            response = requests.post(f"{ES_URL}/arxiv_index/_doc/{UUID}",
                                     json=arxiv_index_body,
                                     headers={'Content-Type': 'application/json'})

            # status_code = response.status_code
            response_data = response.json()

            if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                Log().write_log(f"写入成功 {title_en} - {UUID}", 'info')
            else:
                Log().write_log(f"写入失败 {title_en} - {UUID}", 'error')

            # 写入分类索引

            for i in range(len(classification_zh_list)):
                classification = classification_zh_list[i]
                if classification.startswith(' '):
                    classification = classification[1:]

                classification = (str(classification).replace('(', '（').replace(')', '）')
                                  .replace('  ', '').replace(' ', ''))

                arxiv_paper_classification_zh_body = {
                    "UUID": UUID,
                    "classification_zh": classification,
                    "classification_type": dictionary[classification],
                    "receive_time": receive_time
                }

                response = requests.post(f"{ES_URL}/arxiv_classification_zh/_doc",
                                         json=arxiv_paper_classification_zh_body,
                                         headers={'Content-Type': 'application/json'})

                response_data = response.json()
                if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                    Log().write_log(f"写入分类成功 {classification}", 'info')
                else:
                    Log().write_log(f"写入分类失败 {classification}", 'error')

            # 写入作者索引
            for i in range(len(authors_list)):
                authors = authors_list[i]
                if authors[0:1] == ' ':
                    authors = authors[1:]
                arxiv_paper_authors_body = {
                    "UUID": UUID,
                    "authors": authors,
                    "authors_text": authors,
                    "receive_time": receive_time
                }
                response = requests.post(f"{ES_URL}/arxiv_authors/_doc",
                                         json=arxiv_paper_authors_body,
                                         headers={'Content-Type': 'application/json'})

                response_data = response.json()
                if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                    Log().write_log(f"写入作者成功 {UUID} - {authors}", 'info')
                else:
                    Log().write_log(f"写入作者失败 {UUID} - {authors}", 'error')

            sql = f"UPDATE `Paper`.`index` SET `ES_date` = '{now_time()}', state = '10' WHERE `UUID` = '{UUID}';"
            Date_base().update(sql)

            Log().write_log(f'写入Es成功 {title_zh}', 'info')

    except Exception as e:
        Log().write_log(f'写入Es失败 {UUID}', 'error')
        err1(e)
        time.sleep(3)

