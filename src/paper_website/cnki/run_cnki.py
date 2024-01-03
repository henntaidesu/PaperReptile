import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from src.model.cnki import Crawl, positioned_element
from src.module.log import log
from src.module.read_conf import read_conf
from src.paper_website.cnki.cnki import get_mian_page_info, get_level2_page
from src.module.execution_db import Date_base
import random

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()


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


def open_page(driver, keyword, start_time, end_time):


    # 打开页面，等待两秒
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    random_sleep = round(random.uniform(0, 3), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)
    time_out = 10
    # os.system("pause")

    # 传入关键字
    # WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(keyword)

    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox0'))).click()

    while True:
        time.sleep(2)
        start_yy = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['start_yy']))).text
        start_mm = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['start_mm']))).text
        start_yy = int(start_yy)
        if start_mm == '一月':
            start_mm = 1
        if start_mm == '二月':
            start_mm = 2
        if start_mm == '三月':
            start_mm = 3
        if start_mm == '四月':
            start_mm = 4
        if start_mm == '五月':
            start_mm = 5
        if start_mm == '六月':
            start_mm = 6
        if start_mm == '七月':
            start_mm = 7
        if start_mm == '八月':
            start_mm = 8
        if start_mm == '九月':
            start_mm = 9
        if start_mm == '十月':
            start_mm = 10
        if start_mm == '十一月':
            start_mm = 11
        if start_mm == '十二月':
            start_mm = 12
        print(start_yy)
        print(start_mm, '\n')




        date_list = str(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['start']))).text)[14:]
        date_list = date_list.splitlines()
        # 将每行的内容转化为整数列表
        date_list = [int(line) for line in date_list]

        # 打印结果
        print(date_list)








        time.sleep(3)
        #
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox1'))).click()
        time.sleep(3)

    # 点击搜索
    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()

    print("正在搜索，请稍后...")

    # 获取总文献数和页数
    res_unm = WebDriverWait(driver, time_out).until(
        EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

    # 去除千分位里的逗号
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / 20) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")
    return res_unm


def open_level2_page(driver, keyword):
    # 打开页面，等待两秒
    driver.get(f"https://kns.cnki.net/kns8s/defaultresult/index?korder=TI&kw={keyword}")
    random_sleep = round(random.uniform(0, 1), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)

    print("正在搜索，请稍后...")


def run_paper_main_info(paper_sum_flag):
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    driver = webserver(web_zoom)
    # 设置所需篇数
    start_time = '2024-01-01'
    end_time = '2024-01-01'
    open_page(driver, keyword, start_time, end_time)
    get_mian_page_info(driver, keyword, paper_sum_flag, time_out)
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
