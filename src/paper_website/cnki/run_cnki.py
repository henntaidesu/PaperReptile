import time

import requests

from src.module.execution_db import Date_base
from src.paper_website.cnki.get_cnki_paper_title import get_multi_title_data, get_paper_title
from src.paper_website.cnki.cnki_components import open_paper_info, page_click_sort_type, get_paper_type_number
from src.paper_website.cnki.cnki_components import webserver, open_page_of_title, get_proxy_address
from src.module.log import err2, Log
from src.paper_website.cnki.get_cnki_paper_infomation import get_paper_info


def run_get_paper_title(click_flag, total_page, total_count, None_message):
    try:
        time_out = 3
        driver, proxy_ID, proxy_flag = webserver()
        try:
            res_unm, paper_type, paper_day, date_str, paper_sum = open_page_of_title(driver)
            page_click_sort_type(driver, click_flag)
            flag, total_page, click_flag, total_count, None_message = get_paper_title(driver, res_unm, paper_type,
                                                                                      paper_day, date_str, paper_sum,
                                                                                      total_page, total_count,
                                                                                      click_flag, None_message)
            if flag is False:
                driver.close()
                run_get_paper_title(click_flag, total_page, total_count, None_message)

            else:
                run_get_paper_title(0, 0, 0, False)
        finally:
            driver.close()
    except Exception as e:
        err2(e)


def run_get_paper_info():
    proxy_flag = None
    proxy_ID = None
    time_out = 15
    try:
        while True:
            data = requests.get(f"http://makuro.cn:22023/cnki/get_spider_title").json()
            uuid = data[0]
            title = data[1]
            receive_time = data[2]
            status = data[3]
            db_type = data[4]
            driver, proxy_ID, proxy_flag = webserver()
            page_flag = open_paper_info(driver, title)
            Log().write_log(f"{title} - 共找到 {page_flag}条结果 ", 'info')
            if page_flag > 1:
                sql = f"UPDATE `cnki_index` SET `status` = 'a' WHERE `UUID` = '{uuid}';"
                Date_base().update(sql)
                driver.close()
                continue
            if len(title) < 6:
                sql = f"UPDATE `Paper`.`cnki_index` SET  `status` = '8' WHERE UUID = '{uuid}';"
                Date_base().update(sql)
                driver.close()
            if page_flag is False:
                sql = f"UPDATE `Paper`.`cnki_index` SET  `status` = '9' WHERE UUID = '{uuid}';"
                Date_base().update(sql)
                driver.close()
                continue
            get_flag = get_paper_info(driver, time_out, uuid, title, db_type, receive_time)
    except Exception as e:
        if type(e).__name__ == 'TimeoutException' and proxy_flag is True:
            Log().write_log(f"代理编号{proxy_ID}已失效", 'error')
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '0' where `uuid` = '{uuid}';"
            Date_base().update(sql)
            driver.close()
            run_get_paper_info()
        else:
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '0' where `uuid` = '{uuid}';"
            Date_base().update(sql)
            err2(e)
            run_get_paper_info()
    finally:
        driver.close()


def run_multi_title_data(data):
    for i in data:
        uuid = i[0]
        title = i[1]
        receive_time = i[2]
        # start = i[3]
        db_type = i[4]
        try:
            driver, proxy_ID, proxy_flag = webserver()
            title_number = open_paper_info(driver, title)
            time.sleep(1)
            flag = get_multi_title_data(driver, title_number)
            sql = (f"UPDATE `Paper`.`cnki_index` SET `status` = 'b' "
                   f"WHERE `title` = '{title}' AND `receive_time` = '{receive_time}'")
            Date_base().update(sql)
        except Exception as e:
            err2(e)
        finally:
            driver.close()


def run_multi_title_info(data):
    from src.paper_website.cnki.cnki_components import open_multi_info
    for i in data:
        uuid = i[0]
        title = i[1]
        receive_time = i[2]
        # start = i[3]
        db_type = i[4]
        try:
            driver, proxy_ID, proxy_flag = webserver()
            if_paper = open_multi_info(driver, receive_time, title)
            if if_paper:
                sql = (f"UPDATE `Paper`.`cnki_index` SET `status` = '?' "
                       f"WHERE `title` = '{title}' AND `receive_time` = '{receive_time}'")
                Date_base().update(sql)
                driver.close()
                continue

            get_flag = get_paper_info(driver, 5, uuid, title, db_type, receive_time)
            sql = (f"UPDATE `Paper`.`cnki_index` SET `status` = 'c' "
                   f"WHERE `title` = '{title}' AND `receive_time` = '{receive_time}'")
            Date_base().update(sql)
        finally:
            driver.close()


def run_paper_type_number():
    try:
        driver, proxy_ID, proxy_flag = webserver()
        get_paper_type_number(driver)
    finally:
        driver.close()


