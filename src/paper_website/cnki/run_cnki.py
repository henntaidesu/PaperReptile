import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from src.model.cnki import Crawl, positioned_element, date_choose_start_table, date_choose_end_table
from src.module.log import log
from src.module.read_conf import read_conf
from src.paper_website.cnki.cnki import get_mian_page_info, get_level2_page
from src.module.execution_db import Date_base
from src.module.read_conf import CNKI
from src.module.now_time import year, moon, day1
import random

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()
dts = date_choose_start_table()
dte = date_choose_end_table()


def webserver(web_zoom):
    # get直接返回，不再等待界面加载完成
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    # 设置微软驱动器的环境
    options = webdriver.ChromeOptions()
    # 设置浏览器不加载图片，提高速度
    # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument(f"--force-device-scale-factor={web_zoom}")
    # 创建一个微软驱动器
    driver = webdriver.Chrome(options=options)
    return driver


def setting_select_date(driver, time_out):
    cnki = CNKI()
    yy, mm, dd = cnki.read_cnki_date()
    now_yy = int(year())
    now_mm = int(moon())
    now_day = int(day1())

    paper_day = f"{yy}-{mm}-{dd}"

    flag_page = 0
    flag_yy = now_yy - yy
    flag_page += flag_yy * 12
    flag_mm = now_mm - mm
    flag_page += flag_mm
    # 设置开始时间
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox0'))).click()
    time.sleep(1)
    for i in range(flag_page):
        time.sleep(0.2)
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

    time.sleep(3)

    # 设置结束时间
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox1'))).click()
    for i in range(flag_page):
        time.sleep(0.2)
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


def choose_banner(driver, time_out, paper_day):
    sql = f"select flag from cnki_page_flag WHERE date = '{paper_day}'"
    flag, data = Date_base().select_all(sql)
    if data:
        if data[0] == '0':
            # 点击学术期刊
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['xx']))).click()
            return 0
        if data[1] == '0':
            # 点击学位论文
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['xw']))).click()
            return 1
        if data[2] == '0':
            # 点击会议
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['hy']))).click()
            return 2
        if data[3] == '0':
            # 点击报纸
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['pa']))).click()
            return 3
    else:
        # 判断是否有数据
        xx_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['xx_sum']))).text)
        xw_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['xw_sum']))).text)
        hy_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['hy_sum']))).text)
        pa_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['pa_sum']))).text)
        ts_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['ts_sum']))).text)
        bz_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['bz_sum']))).text)
        cg_sum = int(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['cg_sum']))).text)
        if xx_sum > 0:
            a0 = '0'
        else:
            a0 = '1'

        if xw_sum > 0:
            a1 = '0'
        else:
            a1 = '1'

        if hy_sum > 0:
            a2 = '0'
        else:
            a2 = '1'

        if pa_sum > 0:
            a3 = '0'
        else:
            a3 = '1'

        if ts_sum > 0:
            a5 = '0'
        else:
            a5 = '1'

        if bz_sum > 0:
            a7 = '0'
        else:
            a7 = '1'

        if cg_sum > 0:
            a8 = '0'
        else:
            a8 = '1'

        sql = (f"INSERT INTO `Paper`.`cnki_page_flag`(`date`, `flag`) VALUES "
               f"('{paper_day}', '{a0}{a1}{a2}{a3}0{a5}0{a7}{a8}');")
        Date_base().insert_all(sql)
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['xx']))).click()
        return 0


def open_page(driver, keyword):
    # 打开页面，等待两秒
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    random_sleep = round(random.uniform(0, 3), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)
    time_out = 10
    # os.system("pause")

    # 传入关键字
    # WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(keyword)

    # 设置时间
    paper_day = setting_select_date(driver, time_out)

    # 点击搜索
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()
    time.sleep(2)

    # 切换搜索文章类型
    paper_type = choose_banner(driver, time_out, paper_day)
    time.sleep(2)

    # 切换为每页50条
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['display']))).click()
    time.sleep(2)
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['50']))).click()
    time.sleep(2)


    # 文献数和页数
    res_unm = WebDriverWait(driver, time_out).until(
        EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

    # 去除千分位里的逗号
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / 50) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")

    return res_unm, paper_type, paper_day


def open_level2_page(driver, keyword):
    # 打开页面，等待两秒
    driver.get(f"https://kns.cnki.net/kns8s/defaultresult/index?korder=TI&kw={keyword}")
    random_sleep = round(random.uniform(0, 1), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)

    print("正在搜索，请稍后...")


def run_paper_main_info(paper_sum_flag):
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    yy, mm, dd = CNKI().read_cnki_date()
    driver = webserver(web_zoom)
    # 设置所需篇数
    res_unm, paper_type, paper_day = open_page(driver, keyword)
    date = f"{yy}-{mm}-{dd}"
    flag = get_mian_page_info(driver, keyword, paper_sum_flag, time_out, res_unm, date, paper_type, paper_day)

    if flag is True:
        run_paper_main_info(0)

    driver.close()


def run_lever2_page():
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    driver = webserver(web_zoom)
    while True:
        sql = (f"SELECT cnki_index.UUID, "
               f"cnki_index.title, "
               f"cnki_paper_information.db_type, "
               f"cnki_paper_information.paper_from "
               f"from cnki_index, cnki_paper_information "
               f"WHERE "
               f"cnki_paper_information.db_type IN ('期刊', '博士', '硕士') "
               f"and cnki_index.`start` = '0'  limit 1")

        print(sql)

        flag, data = Date_base().select_all(sql)
        data = data[0]
        uuid = data[0]
        title = data[1]
        db_type = data[2]
        paper_from = data[3]

        open_level2_page(driver, title)
        get_level2_page(driver, keyword, time_out, uuid, title, db_type, paper_from)

        all_handles = driver.window_handles

        # 关闭除第一个窗口以外的所有窗口
        if len(all_handles) > 1:
            start_time = time.time()

        for handle in all_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()
            driver.switch_to.window(all_handles[0])

    # driver.close()
