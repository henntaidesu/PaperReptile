from src.paper_website.cnki.get_cnki_message import get_paper_title, get_paper_info, open_paper_info
from src.paper_website.cnki.cnki_components import webserver, open_page
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from src.module.read_conf import CNKI, read_conf
from src.module.err_message import err
import time


def page_click_sort_type(driver, flag):
    time_out = 5
    try:
        if flag == 0:
            pass
        # 发表时间正序
        time.sleep(3)
        if flag == 1:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
        # 下载正序
        if flag == 2:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        # 下载倒序
        if flag == 3:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
            time.sleep(1)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        # 被引正序
        if flag == 4:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
        # 被引倒序
        if flag == 5:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
            time.sleep(1)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
        # 综合
        if flag == 6:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ZH"]'))).click()
        # 相关度
        if flag == 7:
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="FFD"]'))).click()
    except Exception as e:
        err(e)


def run_get_paper_title(click_flag, total_page, total_count, None_message):
    web_zoom, keyword, papers_need, time_out = read_conf().cnki_paper()
    try:
        driver = webserver(web_zoom)
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        page_click_sort_type(driver, click_flag)
        flag, total_page, click_flag, total_count, None_message = get_paper_title(driver, res_unm, paper_type,
                                                                                  paper_day, date_str,
                                                                                  paper_sum, total_page, total_count,
                                                                                  click_flag, None_message)
        if flag is False:
            driver.close()
            run_get_paper_title(click_flag, total_page, total_count, None_message)

        else:
            driver.close()
            run_get_paper_title(0, 0, 0, False)

    except Exception as e:
        err(e)

    # driver.close()


def run_get_paper_info(date):
    web_zoom, keyword, papers_need, time_out = read_conf().cnki_paper()
    driver = webserver(web_zoom)

    for i in date:
        uuid = i[0]
        title = i[1]
        receive_time = i[2]
        start = i[3]
        db_type = i[4]

        res_unm = open_paper_info(driver, title)
        get_paper_info(driver, time_out, uuid, title, db_type)

    # driver.close()
