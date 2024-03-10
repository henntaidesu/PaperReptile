import sys

from src.module.execution_db import Date_base
from src.module.log import err2


def arxiv_index_data_processing():
    global classification_zh_list
    sql = f"SELECT classification_zh FROM `index` WHERE ES_date is NULL  and `from` = 'arxiv' and classification_zh is not NULL"
    flag, data = Date_base().select_all(sql)
    class_name_list = []
    alist = []
    try:
        for paper_index in data:
            classification_zh = paper_index[0]
            if '；' in classification_zh:
                classification_zh_list = classification_zh.split('；')
            elif ';' in classification_zh:
                classification_zh_list = classification_zh.split(';')
            else:
                if ';' and '；' in classification_zh:
                    print(classification_zh)
                    exit()
                else:
                    classification_zh = (str(classification_zh).replace('(', '（').replace(')', '）')
                                         .replace('  ', '').replace(' ', ''))
                    alist.append(classification_zh)
                    alist = list(set(alist))

            for class_name in classification_zh_list:
                class_name = (str(class_name).replace('(', '（').replace(')', '）')
                              .replace('  ', '').replace(' ', ''))

                class_name_list.append(class_name)
                class_name_list = list(set(class_name_list))

        class_name_list = class_name_list + alist
        class_name_list = list(set(class_name_list))

        for i in class_name_list:
            print(i)
            if i is None:
                continue

            classification_type = 'None'
            if '（math' in i:
                classification_type = '数学'
            if '（数学' in i:
                classification_type = '数学'
            if '（Math' in i:
                classification_type = '数学'

            if '（physical' in i:
                classification_type = '经典物理'
            if '（物理' in i:
                classification_type = '光学物理'
            if '（astro' in i:
                classification_type = '天体物理'
            if '（hep' in i:
                classification_type = '高能物理'
            if '（Quant' in i:
                classification_type = '量子物理'
            if '（Cond-Mat' in i:
                classification_type = '量子物理'
            if '（gr-qc' in i:
                classification_type = '量子物理'
            if '（nucl' in i:
                classification_type = '核物理'
            if '（cond' in i:
                classification_type = '纳米物理'
            if '（nlin' in i:
                classification_type = '生物物理'
            if '（HEP' in i:
                classification_type = '高能物理'

            if '（cs' in i:
                classification_type = '计算机科学'
            if '（Cs' in i:
                classification_type = '计算机科学'
            if '（CS' in i:
                classification_type = '计算机科学'

            if '（q-bio' in i:
                classification_type = '定量生物学'
            if '（q-fin' in i:
                classification_type = '定量金融'
            if '（econ' in i:
                classification_type = '经济学'

            if '（stat' in i:
                classification_type = '统计数据'
            if '（统计' in i:

                classification_type = '统计数据'
            if '（eess' in i:
                classification_type = '电气工程和系统科学'
            sql = (
                f"INSERT INTO `Paper`.`arxiv_classification_type` (`classification_name`, `classification_type`, `flag`)"
                f" VALUES ('{i}', '{classification_type}', '0');")
            Date_base().insert_all(sql)

        exit()
    except Exception as e:
        print(classification_zh)
        err2(e)
        exit()
