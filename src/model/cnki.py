import time

from src.module.execution_db import DB
from src.module.now_time import proxy_time
import requests


def proxy_pool():
    sql = f"SELECT * FROM `proxy_pool` where `status` = '1' and expire_time > '{proxy_time()}' limit 100"
    # sql = f"SELECT * FROM `proxy_pool` where `status` = '1'  and expire_time < '{proxy_time()}' limit 100"
    flag, data = DB().select(sql)
    pool = {}


    for i in range(len(data)):
        ID = data[i][0]
        address = data[i][1]
        port = data[i][2]
        proxy_type = data[i][4]
        pool[i] = f"{proxy_type}://{address}:{port}", f"{ID}"
    return pool


def paper_DB_flag():
    table = {
        0: 'xxkq',
        1: 'xwlw',
        2: 'hy',
        3: 'bz',
        4: 'ts',
        5: 'bs',
        6: 'cg',
        7: 'xxkj',
        8: 'tsqk',
        9: 'sp'
    }
    return table


def paper_DB_DT():
    table = {
        0: "'1'",
        1: "'2'",
        2: "'c'",
        3: "'0'",
        4: "'4'",
        5: "'a'",
        6: "'b'",
        7: "'6'",
        8: "'5'",
        9: "'7'"
    }
    return table


def date_choose_start_table():
    table = {
        1: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[1]',
        2: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[2]',
        3: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[3]',
        4: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[4]',
        5: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[5]',
        6: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[6]',
        7: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[1]/td[7]',
        8: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[1]',
        9: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[2]',
        10: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[3]',
        11: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[4]',
        12: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[5]',
        13: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[6]',
        14: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[2]/td[7]',
        15: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[1]',
        16: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[2]',
        17: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[3]',
        18: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[4]',
        19: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[5]',
        20: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[6]',
        21: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[3]/td[7]',
        22: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[1]',
        23: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[2]',
        24: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[3]',
        25: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[4]',
        26: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[5]',
        27: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[6]',
        28: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[4]/td[7]',
        29: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[1]',
        30: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[2]',
        31: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[3]',
        32: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[4]',
        33: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[5]',
        34: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[6]',
        35: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[5]/td[7]',
        36: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[1]',
        37: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        38: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        39: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        40: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        41: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        42: '/html/body/div[5]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
    }
    return table


def date_choose_end_table():
    table = {
        1: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[1]',
        2: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[2]',
        3: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[3]',
        4: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[4]',
        5: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[5]',
        6: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[6]',
        7: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[1]/td[7]',
        8: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[1]',
        9: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[2]',
        10: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[3]',
        11: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[4]',
        12: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[5]',
        13: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[6]',
        14: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[2]/td[7]',
        15: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[1]',
        16: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[2]',
        17: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[3]',
        18: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[4]',
        19: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[5]',
        20: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[6]',
        21: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[3]/td[7]',
        22: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[1]',
        23: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[2]',
        24: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[3]',
        25: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[4]',
        26: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[5]',
        27: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[6]',
        28: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[4]/td[7]',
        29: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[1]',
        30: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[2]',
        31: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[3]',
        32: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[4]',
        33: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[5]',
        34: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[6]',
        35: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[5]/td[7]',
        36: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[1]',
        37: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        38: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        39: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        40: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        41: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
        42: '/html/body/div[6]/div[1]/div[2]/table/tbody/tr[6]/td[2]',
    }
    return table


def positioned_element():  # 定位元素
    xpaths = {
        'pe': '''div.sort-list''',
        'js': "arguments[0].setAttribute('style', 'display: block;')",
        'ca': 'li[data-val="RP"]',
        'ik': '''//*[@id="gradetxt"]/dd[1]/div[2]/input''',
        'cs': '''//*[@id="ModuleSearch"]/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/div[3]/input''',
        'gn': '''//*[@id="ModuleSearch"]/div[2]/div/div/div/a/em''',
        'display': '''//*[@id="perPageDiv"]/div''',
        '50': '''//*[@id="perPageDiv"]/ul/li[3]/a''',

        0: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[1]/a''',
        'xx_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[1]/a/em''',
        1: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[2]/a''',
        'xw_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[2]/a/em''',
        2: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[3]/a''',
        'hy_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[3]/a/em''',
        3: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[4]/a''',
        'pa_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[4]/a/em''',
        4: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[6]/a''',
        'ts_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[6]/a/em''',
        5: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[8]/a''',
        'bz_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[8]/a/em''',
        6: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[9]/a''',
        'cg_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[9]/a/em''',
        7: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[11]/a''',
        'kj_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[11]/a/em''',
        8: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[17]/a''',
        'tsqk_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[17]/a/em''',
        9: '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[18]/a''',
        'sp_sum': '''//*[@id="ModuleSearch"]/div[2]/div/div/ul/li[18]/a/em''',

        'all_item': '''//*[@id="more"]/i''',

        'start_yy': '''/html/body/div[5]/div[1]/div[1]/div[2]/span''',
        'start_mm': '''/html/body/div[5]/div[1]/div[1]/div[1]/span''',
        'start_previous_page': '''/html/body/div[5]/div[1]/div[1]/button[1]''',
        'start': '''/html/body/div[5]/div[1]/div[2]''',
        'end_yy': '''/html/body/div[6]/div[1]/div[1]/div[2]/span''',
        'end_mm': '''/html/body/div[6]/div[1]/div[1]/div[1]/span''',
        'end_previous_page': '''/html/body/div[6]/div[1]/div[1]/button[1]''',
        'end': '''/html/body/div[6]/div[1]/div[2]''',
    }

    return xpaths


def crawl_xpath():
    xpaths = {
        'abstract': "abstract-text",
        'keywords': "keywords",
        'funds': "funds",
        'catalog': "catalog-list",
        'get_next_page': '''//*[@id='PageNext']''',
        'WebDriverWait': '''//*[@id="ChDivSummaryMore"]''',
        'institute': '//*[@id="authorpart"]/span/a',
        'paper_next_page': '''//*[@id="PageNext"]''',
        'level': '//*[@id="func610"]/div/span',
        'references': '//*[@id="references"]',
        'literature_if_true': '//*[@id="refpartdiv"]/h5/span/b',
        'if_literature_reference': '//*[@id="refpartdiv"]/h5/span/b',
        'year': '//*[@id="divGroup"]/dl[3]',
        'start_time': 'datebox0',
        'end_time': 'datebox1',
        'paper_size1': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[1]''',
        'paper_size2': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[2]''',
        'paper_size3': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[3]''',
        'paper_size4': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[4]''',
        'paper_size5': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[5]''',
        'paper_size6': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[6]''',
        'paper_size7': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[7]''',
        'paper_size8': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[8]''',
        'paper_size9': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[9]''',
    }

    return xpaths


def reference_papers():
    xpaths = {
        # 通用
        'next_page': 'next',
        'paper_num': 'pc_JOURNAL',
        # 期刊
        'journal': 'quotation-journal',
        # 硕士论文
        'master': 'quotation-dissertation-m',
        # 博士论文
        'PhD': 'quotation-dissertation-d',
        # 国际期刊
        'international_journals': 'quotation-journal-w',
        # 图书
        'book': 'quotation-book',
        # 中外文题录
        'Chinese_and_foreign': 'quotation-crldeng',
        # 报纸
        'newpaper': 'quotation-newpaper',
        # 专利
        'patent': 'quotation-patent',
        # 标准
        'standard': 'quotation-stand',
    }

    return xpaths


class QuotePaper:
    @staticmethod
    def reference_name():
        journa = 'journal'
        master = 'master'
        PhD = 'PhD'
        international_journals = 'international_journals'
        book = 'book'
        Chinese_and_foreign = 'Chinese_and_foreign'
        newpaper = 'newpaper'
        patent = 'patent'
        dis = 'standard'
        paper = [journa, master, PhD, international_journals, book, Chinese_and_foreign, newpaper, patent, dis]
        return paper

    @staticmethod
    def paper_list():
        journal = None
        master = None
        PhD = None
        international = None
        book = None
        Chinese_and_foreign = None
        newpaper = None
        patent = None
        dis = None
        paper = [journal, master, PhD, international, book, Chinese_and_foreign, newpaper, patent, dis]
        return paper


class Crawl:
    @staticmethod
    def xpath_inf():
        xpath = "/html/body/div[2]/div[1]/div[3]/div/div/div"
        xpaths = [
            # list
            (f"{xpath}[1]/ul/li[1]/span", f"{xpath}[1]/ul/li[1]/p"),
            (f"{xpath}[1]/ul/li[2]/span", f"{xpath}[1]/ul/li[2]/p"),
            (f"{xpath}[1]/ul/li[3]/span", f"{xpath}[1]/ul/li[3]/p"),
            (f"{xpath}[1]/ul/li[4]/span", f"{xpath}[1]/ul/li[4]/p"),
            (f"{xpath}[1]/ul/li[5]/span", f"{xpath}[1]/ul/li[5]/p"),
            (f"{xpath}[1]/ul/li[6]/span", f"{xpath}[1]/ul/li[6]/p"),
            (f"{xpath}[1]/ul/li[7]/span", f"{xpath}[1]/ul/li[7]/p"),
            (f"{xpath}[1]/ul/li[8]/span", f"{xpath}[1]/ul/li[8]/p"),
            (f"{xpath}[1]/ul/li[9]/span", f"{xpath}[1]/ul/li[9]/p"),

            (f"{xpath}[2]/ul/li[1]/span", f"{xpath}[2]/ul/li[1]/p"),
            (f"{xpath}[2]/ul/li[2]/span", f"{xpath}[2]/ul/li[2]/p"),
            (f"{xpath}[2]/ul/li[3]/span", f"{xpath}[2]/ul/li[3]/p"),
            (f"{xpath}[2]/ul/li[4]/span", f"{xpath}[2]/ul/li[4]/p"),
            (f"{xpath}[2]/ul/li[5]/span", f"{xpath}[2]/ul/li[5]/p"),
            (f"{xpath}[2]/ul/li[6]/span", f"{xpath}[2]/ul/li[6]/p"),
            (f"{xpath}[2]/ul/li[7]/span", f"{xpath}[2]/ul/li[7]/p"),
            (f"{xpath}[2]/ul/li[8]/span", f"{xpath}[2]/ul/li[8]/p"),
            (f"{xpath}[2]/ul/li[9]/span", f"{xpath}[2]/ul/li[9]/p"),

            (f"{xpath}[3]/ul/li[1]/span", f"{xpath}[3]/ul/li[1]/p"),
            (f"{xpath}[3]/ul/li[2]/span", f"{xpath}[3]/ul/li[2]/p"),
            (f"{xpath}[3]/ul/li[3]/span", f"{xpath}[3]/ul/li[3]/p"),
            (f"{xpath}[3]/ul/li[4]/span", f"{xpath}[3]/ul/li[4]/p"),
            (f"{xpath}[3]/ul/li[5]/span", f"{xpath}[3]/ul/li[5]/p"),
            (f"{xpath}[3]/ul/li[6]/span", f"{xpath}[3]/ul/li[6]/p"),
            (f"{xpath}[3]/ul/li[7]/span", f"{xpath}[3]/ul/li[7]/p"),
            (f"{xpath}[3]/ul/li[8]/span", f"{xpath}[3]/ul/li[8]/p"),
            (f"{xpath}[3]/ul/li[9]/span", f"{xpath}[3]/ul/li[9]/p"),

            (f"{xpath}[4]/ul/li[1]/span", f"{xpath}[4]/ul/li[1]/p"),
            (f"{xpath}[4]/ul/li[2]/span", f"{xpath}[4]/ul/li[2]/p"),
            (f"{xpath}[4]/ul/li[3]/span", f"{xpath}[4]/ul/li[3]/p"),
            (f"{xpath}[4]/ul/li[4]/span", f"{xpath}[4]/ul/li[4]/p"),
            (f"{xpath}[4]/ul/li[5]/span", f"{xpath}[4]/ul/li[5]/p"),
            (f"{xpath}[4]/ul/li[6]/span", f"{xpath}[4]/ul/li[6]/p"),
            (f"{xpath}[4]/ul/li[7]/span", f"{xpath}[4]/ul/li[7]/p"),
            (f"{xpath}[4]/ul/li[8]/span", f"{xpath}[4]/ul/li[8]/p"),
            (f"{xpath}[4]/ul/li[9]/span", f"{xpath}[4]/ul/li[9]/p"),

            (f"{xpath}[5]/ul/li[1]/span", f"{xpath}[5]/ul/li[1]/p"),
            (f"{xpath}[5]/ul/li[2]/span", f"{xpath}[5]/ul/li[2]/p"),
            (f"{xpath}[5]/ul/li[3]/span", f"{xpath}[5]/ul/li[3]/p"),
            (f"{xpath}[5]/ul/li[4]/span", f"{xpath}[5]/ul/li[4]/p"),
            (f"{xpath}[5]/ul/li[5]/span", f"{xpath}[5]/ul/li[5]/p"),
            (f"{xpath}[5]/ul/li[6]/span", f"{xpath}[5]/ul/li[6]/p"),
            (f"{xpath}[5]/ul/li[7]/span", f"{xpath}[5]/ul/li[7]/p"),
            (f"{xpath}[5]/ul/li[8]/span", f"{xpath}[5]/ul/li[8]/p"),
            (f"{xpath}[5]/ul/li[9]/span", f"{xpath}[5]/ul/li[9]/p"),

            (f"{xpath}[6]/ul/li[1]/span", f"{xpath}[6]/ul/li[1]/p"),
            (f"{xpath}[6]/ul/li[2]/span", f"{xpath}[6]/ul/li[2]/p"),
            (f"{xpath}[6]/ul/li[3]/span", f"{xpath}[6]/ul/li[3]/p"),
            (f"{xpath}[6]/ul/li[4]/span", f"{xpath}[6]/ul/li[4]/p"),
            (f"{xpath}[6]/ul/li[5]/span", f"{xpath}[6]/ul/li[5]/p"),
            (f"{xpath}[6]/ul/li[6]/span", f"{xpath}[6]/ul/li[6]/p"),
            (f"{xpath}[6]/ul/li[7]/span", f"{xpath}[6]/ul/li[7]/p"),
            (f"{xpath}[6]/ul/li[8]/span", f"{xpath}[6]/ul/li[8]/p"),
            (f"{xpath}[6]/ul/li[9]/span", f"{xpath}[6]/ul/li[9]/p"),

            (f"{xpath}[7]/ul/li[1]/span", f"{xpath}[7]/ul/li[1]/p"),
            (f"{xpath}[7]/ul/li[2]/span", f"{xpath}[7]/ul/li[2]/p"),
            (f"{xpath}[7]/ul/li[3]/span", f"{xpath}[7]/ul/li[3]/p"),
            (f"{xpath}[7]/ul/li[4]/span", f"{xpath}[7]/ul/li[4]/p"),
            (f"{xpath}[7]/ul/li[5]/span", f"{xpath}[7]/ul/li[5]/p"),
            (f"{xpath}[7]/ul/li[6]/span", f"{xpath}[7]/ul/li[6]/p"),
            (f"{xpath}[7]/ul/li[7]/span", f"{xpath}[7]/ul/li[7]/p"),
            (f"{xpath}[7]/ul/li[8]/span", f"{xpath}[7]/ul/li[8]/p"),
            (f"{xpath}[7]/ul/li[9]/span", f"{xpath}[7]/ul/li[9]/p"),

            (f"{xpath}[8]/ul/li[1]/span", f"{xpath}[8]/ul/li[1]/p"),
            (f"{xpath}[8]/ul/li[2]/span", f"{xpath}[8]/ul/li[2]/p"),
            (f"{xpath}[8]/ul/li[3]/span", f"{xpath}[8]/ul/li[3]/p"),
            (f"{xpath}[8]/ul/li[4]/span", f"{xpath}[8]/ul/li[4]/p"),
            (f"{xpath}[8]/ul/li[5]/span", f"{xpath}[8]/ul/li[5]/p"),
            (f"{xpath}[8]/ul/li[6]/span", f"{xpath}[8]/ul/li[6]/p"),
            (f"{xpath}[8]/ul/li[7]/span", f"{xpath}[8]/ul/li[7]/p"),
            (f"{xpath}[8]/ul/li[8]/span", f"{xpath}[8]/ul/li[8]/p"),
            (f"{xpath}[8]/ul/li[9]/span", f"{xpath}[8]/ul/li[9]/p"),

            (f"{xpath}[9]/ul/li[1]/span", f"{xpath}[9]/ul/li[1]/p"),
            (f"{xpath}[9]/ul/li[2]/span", f"{xpath}[9]/ul/li[2]/p"),
            (f"{xpath}[9]/ul/li[3]/span", f"{xpath}[9]/ul/li[3]/p"),
            (f"{xpath}[9]/ul/li[4]/span", f"{xpath}[9]/ul/li[4]/p"),
            (f"{xpath}[9]/ul/li[5]/span", f"{xpath}[9]/ul/li[5]/p"),
            (f"{xpath}[9]/ul/li[6]/span", f"{xpath}[9]/ul/li[6]/p"),
            (f"{xpath}[9]/ul/li[7]/span", f"{xpath}[9]/ul/li[7]/p"),
            (f"{xpath}[9]/ul/li[8]/span", f"{xpath}[9]/ul/li[8]/p"),
            (f"{xpath}[9]/ul/li[9]/span", f"{xpath}[9]/ul/li[9]/p"),

            # 版名
            ("/html/body/div[2]/div[1]/div[3]/div[1]/div/div[5]/span",
             "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[5]/p"),
            # 版号
            ("/html/body/div[2]/div[1]/div[3]/div[1]/div/div[6]/span",
             "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[6]/p"),
        ]

        return xpaths

    @staticmethod
    def xpath_base(term):
        title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[2]'''
        author_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[3]'''
        source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[4]'''
        date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[5]'''
        database_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[6]'''
        quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[7]'''
        download_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[8]'''

        xpaths = [title_xpath, author_xpath, source_xpath, date_xpath, database_xpath, quote_xpath,
                  download_xpath]
        return xpaths
