import sys
import time
import jieba
import requests
from src.module.log import Log, err1
from src.module.execution_db import Date_base
from src.module.read_conf import ReadConf
from src.module.now_time import now_time
from datetime import datetime, timezone, timedelta
from src.model.ES import ArxivModel
import re


def create_cnki_index(data):
    ES_URL = ReadConf().elasticsearch()
    UUID = None

    try:
        for paper_index in data:
            UUID = paper_index[0]
            # UUID = '00ea20fe-ae31-4532-8e7a-d60788c342d9'
            classification_zh = paper_index[3]
            source_language = paper_index[4]
            title_zh = paper_index[5]
            title_en = paper_index[6]
            paper_from = paper_index[9]
            authors = paper_index[11]
            Introduction = paper_index[12]
            receive_time = str(paper_index[13])
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
            if authors:
                authors_list = authors.split(';')
            else:
                authors_list = None

            title_list = jieba.cut(title_zh, cut_all=False)

            # 写入主索引
            index_body = {
                "UUID": UUID,
                "source_language": source_language,
                "title": title_zh,
                "Introduction": Introduction,
                "receive_time": receive_time,
                "size": size,
                "DOI": DOI
            }

            response = requests.post(f"{ES_URL}/cnki_index/_doc/{UUID}",
                                     json=index_body,
                                     headers={'Content-Type': 'application/json'})

            # status_code = response.status_code
            response_data = response.json()

            if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                Log().write_log(f"写入成功主索引 {title_zh}", 'info')
            else:
                Log().write_log(f"写入失败主索引 {title_zh}", 'error')

            # 写入分类索引
            sql = f"SELECT album FROM `Paper`.`cnki_paper_information` WHERE `UUID` = '{UUID}'"
            flag, album = Date_base().select(sql)
            album = album[0][0]

            classification_list = []
            if classification_zh:
                classification_list = classification_zh.split(';')

            if album:
                if ';' in album:
                    album_list = album.split(';')
                    for i in range(len(album_list)):
                        if classification_list:
                            for j in classification_list:
                                album = album_list[i]
                                if album.startswith(' '):
                                    album = album[1:]

                                cnki_paper_album_body = {
                                    "title": title_zh,
                                    "album": album,
                                    "classification": j,
                                    "receive_time": receive_time
                                }

                                response = requests.post(f"{ES_URL}/cnki_album/_doc",
                                                         json=cnki_paper_album_body,
                                                         headers={'Content-Type': 'application/json'})

                                response_data = response.json()
                                if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                                    Log().write_log(f"写入分类成功 {album} -{j}", 'info')
                                else:
                                    Log().write_log(f"写入分类失败 {album}", 'error')

                        else:
                            album = album_list[i]
                            if album.startswith(' '):
                                album = album[1:]

                            cnki_paper_album_body = {
                                "title": title_zh,
                                "album": album,
                                "receive_time": receive_time
                            }

                            response = requests.post(f"{ES_URL}/cnki_album/_doc",
                                                     json=cnki_paper_album_body,
                                                     headers={'Content-Type': 'application/json'})

                            response_data = response.json()
                            if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                                Log().write_log(f"写入分类成功 {album} {j}", 'info')
                            else:
                                Log().write_log(f"写入分类失败 {album}", 'error')

                else:
                    if classification_list:
                        for j in classification_list:
                            cnki_paper_album_body = {
                                "title": title_zh,
                                "album": album,
                                "classification": j,
                                "receive_time": receive_time
                            }
                            response = requests.post(f"{ES_URL}/cnki_album/_doc",
                                                     json=cnki_paper_album_body,
                                                     headers={'Content-Type': 'application/json'})

                            response_data = response.json()
                            if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                                Log().write_log(f"写入分类成功 {album}", 'info')
                            else:
                                Log().write_log(f"写入分类失败 {album}", 'error')


                    else:
                        cnki_paper_album_body = {
                            "title": title_zh,
                            "album": album,
                            "receive_time": receive_time
                        }

                        response = requests.post(f"{ES_URL}/cnki_album/_doc",
                                                 json=cnki_paper_album_body,
                                                 headers={'Content-Type': 'application/json'})

                        response_data = response.json()
                        if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                            Log().write_log(f"写入分类成功 {album}", 'info')
                        else:
                            Log().write_log(f"写入分类失败 {album}", 'error')

            # 写入作者索引
            if authors_list:
                for i in range(len(authors_list)):
                    authors = authors_list[i]
                    if authors[0:1] == ' ':
                        authors = authors[1:]
                    arxiv_paper_authors_body = {
                        "title": title_zh,
                        "authors": authors,
                        "authors_text": authors,
                        "receive_time": receive_time
                    }
                    response = requests.post(f"{ES_URL}/cnki_authors/_doc",
                                             json=arxiv_paper_authors_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入作者成功 - {authors}", 'info')
                    else:
                        Log().write_log(f"写入作者失败 - {authors}", 'error')

            # 写入论文引用索引
            sql = (f"SELECT  `journal`, `master`, `PhD`, `international_journals`, `book`, `Chinese_and_foreign`, "
                   f"`newpaper` FROM `Paper`.`cnki_paper_information` WHERE `UUID` = '{UUID}'")

            flag, data = Date_base().select(sql)
            data = data[0]
            journal = data[0]
            master = data[1]
            PhD = data[2]
            international_journals = data[3]
            book = data[4]
            Chinese_and_foreign = data[5]
            newpaper = data[6]

            if journal:
                journal_list = re.split(r'\d+、', journal)[1:]
                journal_list = [journal.strip(';') for journal in journal_list]
                for album in journal_list:
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": album,
                        "type": '期刊',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入论文期刊引用成功 {album}", 'info')
                    else:
                        Log().write_log(f"写入论文期刊引用失败 {album}", 'error')

            if master:
                master_list = re.split(r'\d+、', master)[1:]
                master_list = [journal.strip(';') for journal in master_list]
                for master in master_list:
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": master,
                        "type": '硕士论文',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入硕士论文引用成功 {master}", 'info')
                    else:
                        Log().write_log(f"写入硕士论文引用失败 {master}", 'error')

            if PhD:
                PhD_list = re.split(r'\d+、', PhD)[1:]
                PhD_list = [journal.strip(';') for journal in PhD_list]
                for PhD in PhD_list:
                    if PhD == 'None':
                        continue
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": PhD,
                        "type": '博士论文',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入博士论文引用成功 {PhD}", 'info')
                    else:
                        Log().write_log(f"写入博士论文引用失败 {PhD}", 'error')

            if international_journals:
                international_journals_list = re.split(r'\d+、', international_journals)[1:]
                international_journals_list = [journal.strip(';') for journal in international_journals_list]
                for international_journals in international_journals_list:
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": international_journals,
                        "type": '国际期刊',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入国际期刊引用成功 {international_journals}", 'info')
                    else:
                        Log().write_log(f"写入国际期刊引用失败 {international_journals}", 'error')

            if book:
                book_list = re.split(r'\d+、', book)[1:]
                book_list = [journal.strip(';') for journal in book_list]
                for book in book_list:
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": book,
                        "type": '图书',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入图书引用成功 {book}", 'info')
                    else:
                        Log().write_log(f"写入图书引用失败 {book}", 'error')

            if Chinese_and_foreign:
                Chinese_and_foreign_list = re.split(r'\d+、', Chinese_and_foreign)[1:]
                Chinese_and_foreign_list = [journal.strip(';') for journal in Chinese_and_foreign_list]
                for Chinese_and_foreign in Chinese_and_foreign_list:
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": Chinese_and_foreign,
                        "type": '中外文题录',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入中外文题录引用成功 {Chinese_and_foreign}", 'info')
                    else:
                        Log().write_log(f"写入博中外文题录引用失败 {Chinese_and_foreign}", 'error')

            if newpaper:
                newpaper_list = re.split(r'\d+、', newpaper)[1:]
                newpaper_list = [journal.strip(';') for journal in newpaper_list]
                for newpaper in newpaper_list:
                    cnki_paper_quote_body = {
                        "title": title_zh,
                        "quote": newpaper,
                        "type": '报纸',
                        "receive_time": receive_time
                    }

                    response = requests.post(f"{ES_URL}/cnki_paper_quote/_doc",
                                             json=cnki_paper_quote_body,
                                             headers={'Content-Type': 'application/json'})

                    response_data = response.json()
                    if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                        Log().write_log(f"写入报纸引用成功 {newpaper}", 'info')
                    else:
                        Log().write_log(f"写入报纸引用失败 {newpaper}", 'error')

            if title_list:
                for a in title_list:
                    for b in classification_list:
                        cnki_title_words_body = {
                            "title": title_zh,
                            "words": a,
                            "classification": b,
                            "receive_time": receive_time
                        }
                        response = requests.post(f"{ES_URL}/cnki_words/_doc",
                                                 json=cnki_title_words_body,
                                                 headers={'Content-Type': 'application/json'})
                        response_data = response.json()
                        if response_data.get('result') == 'created' or response_data.get('result') == 'updated':
                            Log().write_log(f"写入成功 {a} - {b}", 'info')
                        else:
                            Log().write_log(f"写入失败 {a} - {b}", 'error')

            sql = f"UPDATE `Paper`.`index` SET `ES_date` = '{now_time()}', state = '10' WHERE `UUID` = '{UUID}';"
            Date_base().update(sql)

            Log().write_log(f'写入Es成功 {title_zh}', 'info')
            time.sleep(1)

    except Exception as e:
        if str(type(e).__name__) == 'ConnectionError':
            Log().write_log(f'Es已达峰值性能', 'error')
            return False
        else:
            Log().write_log(f'写入Es失败 {UUID}', 'error')
            err1(e)
            time.sleep(3)
