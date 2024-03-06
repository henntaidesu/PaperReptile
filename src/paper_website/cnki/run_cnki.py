from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.module.execution_db import Date_base
from src.paper_website.cnki.get_cnki_paper_title import get_paper_title, open_paper_info, page_click_sort_type
from src.paper_website.cnki.cnki_components import webserver, open_page
from src.module.read_conf import read_conf
from src.module.log import err2
from src.paper_website.cnki.get_cnki_paper_infomation import get_paper_info
from selenium.webdriver.common.by import By


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
        err2(e)

    # driver.close()


def run_get_paper_info(date):
    web_zoom, keyword, papers_need, time_out = read_conf().cnki_paper()

    for i in date:

        uuid = i[0]
        title = i[1]
        # receive_time = i[2]
        # start = i[3]
        db_type = i[4]
        driver = webserver(web_zoom)
        page_flag = open_paper_info(driver, title)
        if len(title) < 6:
            sql = f"UPDATE `Paper`.`cnki_index` SET  `start` = '8' WHERE UUID = '{uuid}';"
            Date_base().update_all(sql)
            driver.close()
        if page_flag is False:
            sql = f"UPDATE `Paper`.`cnki_index` SET  `start` = '9' WHERE UUID = '{uuid}';"
            Date_base().update_all(sql)
            driver.close()
            continue

        get_flag = get_paper_info(driver, time_out, uuid, title, db_type)
        print(get_flag)

    # driver.close()
