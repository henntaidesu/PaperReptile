from src.paper_website.cnki.cnki_components import *
import time
import re
import concurrent.futures
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.module.execution_db import Date_base
from src.module.UUID import UUID
from src.module.now_time import now_time
from src.model.cnki import Crawl, positioned_element, crawl_xpath, reference_papers, QuotePaper
from src.module.log import log
from src.module.read_conf import read_conf
from src.module.err_message import err

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()


def get_paper_title(driver, res_unm, paper_type, paper_day, date_str, paper_sum, total_page, total_count, click_flag, None_message):
    time_out = 5
    count = 1
    title = None
    db_type = None
    authors = None
    source = None
    aa = None
    quote = None
    down_sun = None
    # paper_db = read_conf.cnki_skip_db()
    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()
    new_paper_sum = 0
    sql = None
    dt = None
    xpath_information = crawl_xp.xpath_inf()
    sum_page = res_unm / 50 + 1

    if paper_type == 0:
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `xxkq` = {res_unm} WHERE `date` ='{paper_day}';"
        dt = "'1'"
    elif paper_type == 1:
        dt = "'2', '3'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `xwlw` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 2:
        dt = "'c'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `hy` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 3:
        dt = "'0'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `bz` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 4:
        dt = "'4'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `ts` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 5:
        dt = "'a'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `bs` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 6:
        dt = "'b'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `cg` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 7:
        dt = "'6'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `xxkj` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 8:
        dt = "'5'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `tsqk` = {res_unm} WHERE `date` = '{paper_day}';"
    elif paper_type == 9:
        dt = "'7'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `sp` = {res_unm} WHERE `date` = '{paper_day}';"
    Date_base().update_all(sql)

    sql = (f"SELECT title FROM cnki_index where receive_time >= "
           f"'{paper_day} 00:00:00' and receive_time <= '{paper_day} 23:59:59' and db_type in ({dt})")
    flag, paper_title = Date_base().select_all(sql)

    len_data = len(paper_title)

    issuing_time_flag = False
    None_message = False
    if res_unm > 5950:
        issuing_time_flag = True

    # 当爬取数量小于需求时，循环网页页码
    while True:
        total_page += 1
        print(f'total_page   :   {total_page}')
        if issuing_time_flag is True and None_message is False:
            if total_page == 120:
                # 按引用倒序
                return False, total_page, 1, count, False

            if total_page == 240 and res_unm > 8000:
                # 按下载正序
                return False, total_page, 2, count, False

            if total_page == 360 and res_unm > 10000:
                # 按引用正序
                return False, total_page, 3, count, False

            if total_page == 480 and res_unm > 12000:
                return False, total_page, 4, count, False
                # 按下载倒序
            if total_page == 600 and res_unm > 15000:
                # 按发表顺序倒
                return False, total_page, 5, count, False

            if total_page == 720 and res_unm > 18000:
                # 按发表顺序倒
                return False, total_page, 6, count, False

            if total_page == 840 and res_unm > 21000:
                # 按发表顺序倒
                return False, total_page, 7, count, False

            if total_page == 960:
                flag333 = whit_file(date_str, paper_type, paper_day)
                if flag333 is True:
                    return True, False, -1, count, False
        # 等待加载完全，休眠1S
        time.sleep(1)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 循环网页一页中的条目
        for i in range((count - 1) % paper_sum + 1, paper_sum + 1):
            print(f"{res_unm} --- {count + len_data - new_paper_sum} --- {total_page}")
            if res_unm < count + len_data - new_paper_sum or total_page > sum_page:
                logger.write_log("已获取完数据")
                flag333 = whit_file(date_str, paper_type, paper_day)
                if flag333 is True:
                    return True, False, -1, count, False
            print(f"正在爬取第{count + len_data - new_paper_sum}条基础数据,跳过{new_paper_sum}"
                  f"条(第{(count - 1) // paper_sum + 1}页第{i}条 总第{total_count + count}次查询 共{res_unm}条):")

            try:
                term = (count - 1) % paper_sum + 1  # 本页的第几个条目
                xpaths = crawl_xp.xpath_base(term)

                try:
                    if res_unm == 1:
                        xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[2]/a'''
                        title = WebDriverWait(driver, time_out).until(
                            EC.presence_of_element_located((By.XPATH, xpath))).text

                    else:
                        xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i}]/td[2]/a'''
                        title = WebDriverWait(driver, time_out).until(
                            EC.presence_of_element_located((By.XPATH, xpath))).text
                except Exception as e:
                    xpath = f'''//*[@id="briefBox"]/p'''
                    title = WebDriverWait(driver, time_out).until(
                        EC.presence_of_element_located((By.XPATH, xpath))).text
                    if title == '抱歉，暂无数据，请稍后重试。' and issuing_time_flag is True and total_page % 120 != 0:
                        None_message = True
                        return False, total_page, click_flag + 1, count, None_message

                if '增强出版' in title:
                    title = title[:-5]

                if '网络首发' in title:
                    title = title[:-5]

                if_title = None
                for ii in paper_title:
                    if ii[0] == title:
                        print(f"数据已存在 : {title}")
                        if_title = True
                        break

                if if_title is True:
                    new_paper_sum += 1
                    if i == 50:
                        time.sleep(3)
                    continue

                if paper_type == 0:
                    # 期刊
                    db_type = '1'

                elif paper_type == 2:
                    # 会议
                    db_type = 'c'

                elif paper_type == 3:
                    # 报纸
                    db_type = '0'

                elif paper_type == 4:
                    # 图书
                    db_type = '4'

                elif paper_type == 5:
                    # 标准
                    db_type = 'a'

                elif paper_type == 6:
                    # 成果
                    db_type = 'b'

                elif paper_type == 7:
                    # 辑刊
                    db_type = '6'

                elif paper_type == 8:
                    # 特色期刊
                    db_type = '5'

                elif paper_type == 9:
                    # 视频
                    db_type = '7'

                elif db_type == '硕士':
                    db_type = '2'

                elif db_type == '博士':
                    db_type = '3'

                else:
                    db_type = '9'

                title = TrimString(title)
                uuid = UUID()
                sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                        f"(`UUID`, `title`, `receive_time`, `start`, `db_type`) "
                        f"VALUES ('{uuid}', '{title}', '{paper_day}', '0', '{db_type}');")

                sql3 = TrSQL(sql3)
                flag = Date_base().insert_all(sql3)
                if flag == '重复数据':
                    new_paper_sum += 1
                    logger.write_log(f"重复数据 ： {title}, UUID : {uuid}")
                    continue

                print(f"\n标题:    {title}\n")

                logger.write_log(f"已获取 ： {title}, UUID : {uuid}")

            except Exception as e:
                err(e)
                if type(e).__name__ == 'TimeoutException' and issuing_time_flag is False:
                    print(f"{res_unm} ------- {count + len_data - new_paper_sum + 1}")
                    logger.write_log(f"已获取完数据 ，，{res_unm - (count + len_data - new_paper_sum + 1)}条数据无法获取")
                    flag333 = whit_file(date_str, paper_type, paper_day)
                    if flag333 is True:
                        return True, False, -1, count, False

            finally:
                count += 1
            continue_flag = False
            if res_unm <= count + len_data - new_paper_sum - 1:
                logger.write_log("已获取完数据")

                flag333 = whit_file(date_str, paper_type, paper_day)

                if flag333 is True:
                    return True, False, -1, count, False
            # time.sleep(1)

        try:
            time.sleep(2)
            ActionChains(driver).key_down(Keys.ARROW_RIGHT).key_up(Keys.ARROW_RIGHT).perform()
        except Exception as e:
            err(e)


