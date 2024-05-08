import sys
import time
import requests
from src.module.execution_db import Date_base
from src.paper_website.cnki.get_cnki_paper_title import get_multi_title_data, get_paper_title
from src.paper_website.cnki.cnki_components import open_paper_info, page_click_sort_type, get_paper_type_number
from src.paper_website.cnki.cnki_components import webserver, open_page_of_title, get_spider_paper_title
from src.paper_website.cnki.get_cnki_paper_infomation import get_paper_info
from src.paper_website.cnki.cnki_components import open_multi_info, get_title_data_is_none
from src.module.log import err2, Log
from src.module.rabbitMQ import rabbitmq_consume

logger = Log()


def run_get_paper_title(click_flag, total_page, total_count, None_message):
    driver, proxy_ID, proxy_flag = webserver()
    try:
        sql = f"SELECT `date`, flag FROM cnki_page_flag WHERE flag != '1111111111' ORDER BY `date` DESC LIMIT 1"
        flag, data = Date_base().select(sql)

        paper_day = data[0][0]
        paper_flag = data[0][1]

        res_unm, paper_type, paper_day, date_str, paper_sum = open_page_of_title(driver, paper_day, paper_flag)
        if res_unm:
            page_click_sort_type(driver, click_flag)
            flag, total_page, click_flag, total_count, None_message = get_paper_title(driver, res_unm, paper_type,
                                                                                      paper_day, date_str, paper_sum,
                                                                                      total_page, total_count,
                                                                                      click_flag, None_message)

        else:
            get_title_data_is_none(paper_flag, paper_day)
            return False

        if flag is False:
            driver.close()
            run_get_paper_title(click_flag, total_page, total_count, None_message)

        else:
            try:
                all_handles = driver.window_handles
                for handle in all_handles:
                    driver.switch_to.window(handle)
                    driver.close()
            finally:
                pass

            run_get_paper_title(0, 0, 0, False)

    except Exception as e:
        err2(e)
    finally:
        all_handles = driver.window_handles
        for handle in all_handles:
            driver.switch_to.window(handle)
            driver.close()


def run_get_paper_info():
    time_out = 10
    queue_name = "paper_title_status=0"
    while True:
        proxy_flag = None
        proxy_ID = None
        driver = None
        uuid = None
        try:
            data = rabbitmq_consume(queue_name)
            if data is None:
                logger.write_log("队列无数据", 'warning')
                time.sleep(60)
                return

            data = [item.strip() for item in data.split(',')]

            uuid = data[0]
            title = data[1]
            receive_time = data[2]
            status = data[3]
            db_type = data[4]

            if len(title) < 6:
                sql = f"UPDATE `Paper`.`cnki_index` SET  `status` = '8' WHERE UUID = '{uuid}';"
                Date_base().update(sql)
            else:
                driver, proxy_ID, proxy_flag = webserver()
                page_flag = open_paper_info(driver, title)
                logger.write_log(f"{title} - 共找到 {page_flag}条结果 ", 'info')
                if page_flag > 1:
                    sql = f"UPDATE `cnki_index` SET `status` = 'a' WHERE `UUID` = '{uuid}';"
                    Date_base().update(sql)
                elif page_flag is False:
                    sql = f"UPDATE `Paper`.`cnki_index` SET  `status` = '9' WHERE UUID = '{uuid}';"
                    Date_base().update(sql)
                else:
                    flag = get_paper_info(driver, time_out, uuid, title, db_type, receive_time)
                    if flag is False:
                        sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '0' where `uuid` = '{uuid}';"
                        Date_base().update(sql)
        except Exception as e:
            if type(e).__name__ == 'WebDriverException' and proxy_flag is True:
                logger.write_log(f"代理编号{proxy_ID}错误", 'error')
                # sql = f"UPDATE `Paper`.`proxy_pool` SET `status` = 'D' WHERE `id` = {proxy_ID};"
                # Date_base().update(sql)
                sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '0' where `uuid` = '{uuid}';"
                Date_base().update(sql)
            elif type(e).__name__ == 'TimeoutException' and proxy_flag is True:
                logger.write_log(f"代理编号{proxy_ID}超时", 'error')
                sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '0' where `uuid` = '{uuid}';"
                Date_base().update(sql)
            else:
                sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '0' where `uuid` = '{uuid}';"
                Date_base().update(sql)
                err2(e)
        finally:
            all_handles = driver.window_handles
            for handle in all_handles:
                driver.switch_to.window(handle)
                driver.close()


def run_multi_title_data():
    driver = None
    time_out = 10
    queue_name = "paper_title_status=a"

    driver, proxy_ID, proxy_flag = webserver()

    data = rabbitmq_consume(queue_name)
    if data is None:
        logger.write_log("队列无数据", 'warning')
        time.sleep(60)
        return

    data = [item.strip() for item in data.split(',')]

    uuid = data[0]
    title = data[1]
    receive_time = data[2]
    status = data[3]
    db_type = data[4]
    logger.write_log(f"当前获取 - {title}", 'info')
    try:
        title_number = open_paper_info(driver, title)
        time.sleep(1)
        flag = get_multi_title_data(driver, title_number, time_out)
        if flag is True:
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'b' where `uuid` = '{uuid}'"
        else:
            logger.write_log(f"{title} - {uuid} - 获取错误", 'error')
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'a' where `uuid` = '{uuid}'"
        Date_base().update(sql)
    except Exception as e:
        if type(e).__name__ == 'TimeoutException':
            logger.write_log(f"{title} 获取超时", 'error')
        else:
            err2(e)
        sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'a' where `uuid` = '{uuid}'"
        Date_base().update(sql)
    finally:
        all_handles = driver.window_handles
        for handle in all_handles:
            driver.switch_to.window(handle)
            driver.close()


def run_multi_title_info():
    driver = None
    time_out = 10
    queue_name = "paper_title_status=b"

    driver, proxy_ID, proxy_flag = webserver()
    try:
        data = rabbitmq_consume(queue_name)
        if data is None:
            logger.write_log("队列无数据", 'warning')
            time.sleep(60)
            return

        data = [item.strip() for item in data.split(',')]

        uuid = data[0]
        title = data[1]
        receive_time = data[2]
        status = data[3]
        db_type = data[4]

        if_paper = open_multi_info(driver, receive_time, title, time_out)
        if if_paper:
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '?'  where `uuid` = '{uuid}' "
            Date_base().update(sql)

        get_flag = get_paper_info(driver, time_out, uuid, title, db_type, receive_time)
        if get_flag:
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = '1'  where `uuid` = '{uuid}' "
        else:
            sql = f"UPDATE `Paper`.`cnki_index` SET `status` = 'b'  where `uuid` = '{uuid}' "
        Date_base().update(sql)
    finally:
        all_handles = driver.window_handles
        for handle in all_handles:
            driver.switch_to.window(handle)
            driver.close()


def run_paper_type_number():
    try:
        driver, proxy_ID, proxy_flag = webserver()
        get_paper_type_number(driver)
    finally:
        driver.close()
