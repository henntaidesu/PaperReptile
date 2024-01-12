import time
import re
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.module.execution_db import Date_base
from src.module.read_conf import CNKI

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import concurrent.futures
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.module.UUID import UUID
from src.module.now_time import now_time
from src.model.cnki import Crawl, positioned_element, crawl_xpath, reference_papers, QuotePaper
from src.module.log import log
from src.module.err_message import err


def TrimString(Str):
    if '\n' in Str:
        Str = Str.replace('\n', ' ')
    # if ' ' in Str:
    #     Str = Str.replace(' ', '')
    # if '/' in Str:
    #     Str = Str.replace('/', ' ')
    if "'" in Str:
        Str = Str.replace("'", "\\'")
    if '"' in Str:
        Str = Str.replace('"', '\\"')
    return Str


def Trim_passkey(Str):
    Str = Str.replace(";", " ")
    return Str


def trim_quote(Str):
    Str = str(Str)
    Str = Str.replace(',', '').replace("'", "").replace('] ', '、')
    Str = Str.replace(' ', '')[2:][:-1]
    return Str


def extract_number(item):
    match = re.search(r"(\d+)\]", item)
    return int(match.group(1)) if match else float('inf')


def TrSQL(sql):
    sql = sql.replace("None", "NULL").replace("'NULL'", "NULL")
    return sql


def get_info(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text
    except:
        return None


def is_english_string(s):
    # 使用正则表达式判断字符串是否全为英文字符
    return bool(re.match('''^[a-zA-Z\s.,;:!?\'"()]+$''', s))


def get_choose_info(driver, xpath1, xpath2, str):
    try:
        if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath1))).text == str:
            return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath2))).text
        else:
            return None
    except:
        return None


def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False


def revise_cnki_date():
    cnki = CNKI()
    yy, mm, dd = cnki.read_cnki_date()
    dd -= 1
    if dd == 0:
        mm -= 1
        if mm in {1, 3, 5, 7, 8, 10, 12}:
            dd = 31
        elif mm == 2:
            if (yy % 4 == 0 and yy % 100 != 0) or (yy % 400 == 0):
                dd = 29
            else:
                dd = 28
        elif mm == 0:
            yy -= 1
            mm = 12
            dd = 31
        else:
            dd = 30

    cnki.write_cnki_date(str(yy), str(mm), str(dd))
    return True


def whit_file(date_str, paper_type, paper_day):
    date_str = list(date_str)
    date_str[paper_type] = '1'
    date_str = str(date_str)
    date_str = date_str[1:][:-1].replace(',', '').replace("'", "").replace(" ", "")
    flag = False
    sql = f"UPDATE `Paper`.`cnki_page_flag` SET `flag` = '{date_str}' WHERE `date` = '{paper_day}'"
    Date_base().update_all(sql)
    if date_str == '1111111111':
        flag = revise_cnki_date()
    else:
        return True

    if flag is True:
        return True
