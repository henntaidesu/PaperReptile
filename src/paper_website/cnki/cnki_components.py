import time
import re
import random
import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.module.execution_db import Date_base
from src.module.read_conf import CNKI, read_conf
from src.model.cnki import date_choose_end_table, date_choose_start_table
from src.module.now_time import year, moon, day
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from src.model.cnki import Crawl, positioned_element
from src.module.log import Log, err2
from concurrent.futures import ThreadPoolExecutor

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = Log()
read_conf = read_conf()
dts = date_choose_start_table()
dte = date_choose_end_table()


def webserver():
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    options = webdriver.ChromeOptions()
    # 设置浏览器不加载图片，提高速度
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument("--disable-gpu")
    options.add_argument('--headless')  # 不唤起实体浏览器
    options.add_argument('--log-level=3')  # 设置日志级别减少输出信息
    options.add_argument('--silent')  # 完全禁止 DevTools 输出
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用 DevTools 监听输出

    # proxy_flag, proxy_url = read_conf.cnki_proxy()
    # if proxy_flag is True:
    #     proxy = Proxy()
    #     proxy.proxy_type = ProxyType.MANUAL
    #     proxy.http_proxy = proxy_url
    #     options.add_argument(f"--proxy-server={proxy.http_proxy}")

    # 指定chromedriver.exe的位置
    driver = webdriver.Chrome(service=ChromeService(r"chromedriver.exe"), options=options)
    return driver


def setting_select_date(driver, time_out):
    try:
        cnki = CNKI()
        yy, mm, dd = cnki.read_cnki_date()
        now_yy = int(year())
        now_mm = int(moon())
        now_day = int(day())

        paper_day = f"{yy}-{mm}-{dd}"

        flag_page = 0
        flag_yy = now_yy - yy
        flag_page += flag_yy * 12
        flag_mm = now_mm - mm
        flag_page += flag_mm

        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox0'))).click()
        time.sleep(1)
        for i in range(flag_page):
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located
                                                  ((By.XPATH, open_page_data['start_previous_page']))).click()

        time.sleep(1)

        date_list = str(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['start']))).text)[14:]
        date_list = date_list.splitlines()
        # 将每行的内容转化为整数列表
        date_list = [int(line) for line in date_list]
        list_flag = 0
        list_flag = date_list.index(1)

        while True:
            list_flag += 1
            if dd == date_list[list_flag - 1]:
                break

        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, dts[list_flag]))).click()

        time.sleep(2)

        # 设置结束时间
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox1'))).click()
        time.sleep(1)
        for i in range(flag_page):
            # time.sleep(0.5)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located
                                                  ((By.XPATH, open_page_data['end_previous_page']))).click()

        time.sleep(2)

        date_list = str(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['end']))).text)[14:]
        date_list = date_list.splitlines()
        # 将每行的内容转化为整数列表
        date_list = [int(line) for line in date_list]
        list_flag = 0
        list_flag = date_list.index(1)
        while True:
            list_flag += 1
            if dd == date_list[list_flag - 1]:
                break
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, dte[list_flag]))).click()
        time.sleep(2)

        return paper_day
    except Exception as e:
        err2(e)


def choose_banner(driver, time_out, paper_day):
    sql = f"select flag from cnki_page_flag WHERE date = '{paper_day}'"
    flag, data = Date_base().select(sql)
    if data:
        date_temp = data[0][0]
        data = data[0][0]
        if data == '1111111111':
            # logger.write_log(f'今日已获取{data}')
            revise_cnki_date()
            driver.close()
            choose_banner(driver, time_out, paper_day)
        # print(data)
        data = list(data)
        # print(data)

        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['all_item']))).click()
        time.sleep(3)

        for i in range(9):
            if data[i] == '0':
                WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.XPATH, open_page_data[i]))).click()
                return i, date_temp

    else:
        # 判断是否有数据
        xx_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['xx_sum']))).text
        xw_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['xw_sum']))).text
        hy_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['hy_sum']))).text
        pa_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['pa_sum']))).text
        ts_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['ts_sum']))).text
        bz_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['bz_sum']))).text
        cg_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['cg_sum']))).text
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['all_item']))).click()
        time.sleep(2)
        kj_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['kj_sum']))).text
        tsqk_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['tsqk_sum']))).text
        sp_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['sp_sum']))).text

        if '万' in xx_sum:
            xx_sum = int(f"{xx_sum[:-1].replace('.', '')}00")
        else:
            xx_sum = int(xx_sum)
        if xx_sum > 0:
            a0 = '0'
        else:
            a0 = '1'

        if '万' in xw_sum:
            xw_sum = int(f"{xw_sum[:-1].replace('.', '')}00")
        else:
            xw_sum = int(xw_sum)
        if xw_sum > 0:
            a1 = '0'
        else:
            a1 = '1'

        if '万' in hy_sum:
            hy_sum = int(f"{hy_sum[:-1].replace('.', '')}00")
        else:
            hy_sum = int(hy_sum)
        if hy_sum > 0:
            a2 = '0'
        else:
            a2 = '1'

        if '万' in pa_sum:
            pa_sum = int(f"{pa_sum[:-1].replace('.', '')}00")
        else:
            pa_sum = int(pa_sum)
        if pa_sum > 0:
            a3 = '0'
        else:
            a3 = '1'

        if '万' in ts_sum:
            ts_sum = int(f"{ts_sum[:-1].replace('.', '')}00")
        else:
            ts_sum = int(ts_sum)
        if ts_sum > 0:
            a5 = '0'
        else:
            a5 = '1'

        if '万' in bz_sum:
            bz_sum = int(f"{bz_sum[:-1].replace('.', '')}00")
        else:
            bz_sum = int(bz_sum)
        if bz_sum > 0:
            a7 = '0'
        else:
            a7 = '1'

        if '万' in cg_sum:
            cg_sum = int(f"{cg_sum[:-1].replace('.', '')}00")
        else:
            cg_sum = int(cg_sum)
        if cg_sum > 0:
            a8 = '0'
        else:
            a8 = '1'

        if '万' in kj_sum:
            kj_sum = int(f"{kj_sum[:-1].replace('.', '')}00")
        else:
            kj_sum = int(kj_sum)
        if kj_sum > 0:
            a9 = '0'
        else:
            a9 = '1'

        if '万' in tsqk_sum:
            tsqk_sum = int(f"{tsqk_sum[:-1].replace('.', '')}00")
        else:
            tsqk_sum = int(tsqk_sum)
        if tsqk_sum > 0:
            a10 = '0'
        else:
            a10 = '1'

        if '万' in sp_sum:
            sp_sum = int(f"{sp_sum[:-1].replace('.', '')}00")
        else:
            sp_sum = int(sp_sum)
        if sp_sum > 0:
            a11 = '0'
        else:
            a11 = '1'

        item_flag = f"{a0}{a1}{a2}{a3}{a5}{a7}{a8}{a9}{a10}{a11}"

        sql = (f"INSERT INTO `Paper`.`cnki_page_flag`"
               f"(`date`, `flag`, `xxkq`, `xwlw`, `hy`, `bz`, `ts`, `bs`, `cg`, `xxkj`, `tsqk`, `sp`) "
               f"VALUES ('{paper_day}', '{item_flag}', '{xx_sum}', '{xw_sum}', '{hy_sum}', '{pa_sum}', '{ts_sum}', "
               f"'{bz_sum}', '{cg_sum}', '{kj_sum}', '{tsqk_sum}', '{sp_sum}');").replace("'0'", "NULL")

        Date_base().insert(sql)
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data[0]))).click()
        return 0, item_flag


def open_page_of_title(driver):
    # 打开页面，等待两秒
    try:
        url = f"https://kns.cnki.net/kns8/AdvSearch"
        driver.get(url)
        time_out = 10
        time.sleep(3)
        # 设置时间
        paper_day = setting_select_date(driver, time_out)

        # 点击搜索
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()
        time.sleep(2)

        # 切换搜索文章类型
        paper_type, date_str = choose_banner(driver, time_out, paper_day)
        time.sleep(5)

        # 文献数和页数
        res_unm = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

        res_unm = int(res_unm.replace(",", ''))
        if res_unm > 5950:
            # 按发表顺序正
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
            time.sleep(2)
        if res_unm > 49:
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['display']))).click()
            time.sleep(2)
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['50']))).click()
            time.sleep(2)

        paper_sum = 50

        print(f"共找到 {res_unm} 条结果, {int(res_unm / paper_sum + 1)} 页。")
        return res_unm, paper_type, paper_day, date_str, paper_sum
    except Exception as e:
        err2(e)


def open_paper_info(driver, keyword):
    time_out = 5
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(
        keyword)

    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()
    time.sleep(2)

    try:
        res_unm = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text
    except:
        return False

    paper_sum = 20
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / paper_sum) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")
    return res_unm


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


def process_element(driver, div, li):
    xpath1 = f"/html/body/div[2]/div[1]/div[3]/div/div/div[{div}]/ul/li[{li}]/span"
    xpath2 = f"/html/body/div[2]/div[1]/div[3]/div/div/div[{div}]/ul/li[{li}]/p"
    try:
        class_name_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath1)))
        class_name = class_name_elem.text
        if class_name:
            class_data_elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath2)))
            class_data = class_data_elem.text
            return class_name, class_data
    except:
        return None


def get_choose_info(driver):
    class_list = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for div in range(3, 9):
            for li in range(1, 9):
                futures.append(executor.submit(process_element, driver, div, li))
        for future in futures:
            result = future.result()
            if result:
                class_list.append(result)
    return class_list


def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False


def revise_cnki_date():
    cnki = CNKI()
    yy, mm, dd = cnki.read_cnki_date()
    dd += 1
    if mm in {1, 3, 5, 7, 8, 10} and dd > 31:
        dd = 1

    elif mm in {2, 4, 6, 9, 11} and dd > 30:
        dd = 1

    elif mm == 2:
        if (yy % 4 == 0 and yy % 100 != 0) or (yy % 400 == 0):
            if dd > 29:
                dd = 1
        else:
            if dd > 28:
                dd = 1

    elif mm == 12 and dd > 31:
        yy += 1
        mm = 1
        dd = 1

    cnki.write_cnki_date(str(yy), str(mm), str(dd))
    return True


def revise_cnki_date1():
    cnki = CNKI()
    yy, mm, dd = cnki.read_cnki_date()
    dd += 1
    if dd == 0:
        mm += 1
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
    sql = f"UPDATE `Paper`.`cnki_page_flag` SET `flag` = '{date_str}' WHERE `date` = '{paper_day}'"
    Date_base().update(sql)
    if date_str == '1111111111':
        flag = revise_cnki_date()
    else:
        return True

    if flag is True:
        return True


def page_click_sort_type(driver, flag):
    time_out = 5
    try:
        # 被引正序
        if flag == 0:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CF"]'))).click()
        # 下载正序
        time.sleep(3)
        if flag == 1:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        # 发表时间正序
        if flag == 2:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        # 被引倒序
        if flag == 3:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CF"]'))).click()
            time.sleep(1)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CF"]'))).click()
        # 下载倒序
        if flag == 4:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
            time.sleep(1)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        # 发表时间倒序
        if flag == 5:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
            time.sleep(1)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
        # 相关度
        if flag == 6:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="FFD"]'))).click()
        # 综合
        if flag == 7:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ZH"]'))).click()
    except ExceptionGroup as e:
        err2(e)
