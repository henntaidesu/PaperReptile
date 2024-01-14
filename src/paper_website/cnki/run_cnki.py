from src.paper_website.cnki.get_cnki_paper_title import get_paper_title, open_paper_info, page_click_sort_type
from src.paper_website.cnki.cnki_components import webserver, open_page
from src.module.read_conf import read_conf
from src.module.err_message import err
from src.paper_website.cnki.get_cnki_paper_infomation import get_paper_info


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
        # receive_time = i[2]
        # start = i[3]
        db_type = i[4]

        open_paper_info(driver, title)
        get_paper_info(driver, time_out, uuid, title, db_type)

        all_handles = driver.window_handles
        if len(all_handles) > 1:
            pass

        for handle in all_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()
            driver.switch_to.window(all_handles[0])

    # driver.close()
