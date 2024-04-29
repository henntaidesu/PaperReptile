import time
from src.module.execution_db import Date_base
from src.paper_website.cnki.get_cnki_paper_title import get_multi_title_data, get_paper_title
from src.paper_website.cnki.cnki_components import open_paper_info, page_click_sort_type, get_paper_type_number
from src.paper_website.cnki.cnki_components import webserver, open_page_of_title, get_proxy_address
from src.module.log import err2, Log
from src.paper_website.cnki.get_cnki_paper_infomation import get_paper_info


def run_get_paper_title(click_flag, total_page, total_count, None_message):
    try:
        time_out = 3
        proxy, ID = get_proxy_address()
        driver = webserver(proxy)
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
                driver.close()
                run_get_paper_title(0, 0, 0, False)
        finally:
            driver.close()
            sql = f"UPDATE `Paper`.`proxy_pool` SET `status` = '0' WHERE `id` = {ID};"
            Date_base().update(sql)
    except Exception as e:
        err2(e)


def run_get_paper_info(data):
    time_out = 3
    for i in data:
        uuid = i[0]
        title = i[1]
        receive_time = i[2]
        # start = i[3]
        db_type = i[4]
        proxy, ID = get_proxy_address()
        driver = webserver(proxy)
        try:
            page_flag = open_paper_info(driver, title)
            Log().write_log(f"{title} - 共找到 {page_flag}条结果 ", 'info')
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
            err2(e)
        finally:
            driver.close()
            sql = f"UPDATE `Paper`.`proxy_pool` SET `status` = '0' WHERE `id` = {ID};"


def run_multi_title_data(data):
    for i in data:
        uuid = i[0]
        title = i[1]
        receive_time = i[2]
        # start = i[3]
        db_type = i[4]
        try:

            proxy, ID = get_proxy_address()
            driver = webserver(proxy)
            title_number = open_paper_info(driver, title)
            time.sleep(1)
            flag = get_multi_title_data(driver, title_number)
            sql = (f"UPDATE `Paper`.`cnki_index` SET `status` = 'b' "
                   f"WHERE `title` = '{title}' AND `receive_time` = '{receive_time}'")
            Date_base().update(sql)
        except Exception as e:
            err2(e)
        finally:
            sql = f"UPDATE `Paper`.`proxy_pool` SET `status` = '0' WHERE `id` = {ID};"
            Date_base().update(sql)
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
            proxy, ID = get_proxy_address()
            driver = webserver(proxy)
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
            driver.close()
        finally:
            sql = f"UPDATE `Paper`.`proxy_pool` SET `status` = '0' WHERE `id` = {ID};"
            Date_base().update(sql)
            driver.close()


def run_paper_type_number():
    try:
        proxy, ID = get_proxy_address()
        driver = webserver(proxy)
        get_paper_type_number(driver)
    finally:
        sql = f"UPDATE `Paper`.`proxy_pool` SET `status` = '0' WHERE `id` = {ID};"
        Date_base().update(sql)
        driver.close()


