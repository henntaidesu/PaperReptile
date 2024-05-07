from src.paper_website.cnki.cnki_components import *
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.module.execution_db import Date_base
from src.module.UUID import UUID
from src.model.cnki import Crawl, positioned_element, paper_DB_flag, paper_DB_DT
from src.module.log import Log, err2, err3
from src.module.read_conf import ReadConf

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = Log()
read_conf = ReadConf()


def get_paper_title(driver, res_unm, paper_type, paper_day, date_str, paper_sum, total_page, total_count, click_flag,
                    None_message):
    time_out = 5
    count = 1
    new_paper_sum = 0

    sql = f"UPDATE `cnki_page_flag` SET `{paper_DB_flag()[paper_type]}` = {res_unm} WHERE `date` ='{paper_day}';"
    Date_base().update(sql)

    sql = (f"SELECT title FROM cnki_index where receive_time >= '{paper_day} 00:00:00' "
           f"and receive_time <= '{paper_day} 23:59:59' and db_type in ({paper_DB_DT()[paper_type]})")
    flag, paper_title = Date_base().select(sql)

    len_data = len(paper_title)

    issuing_time_flag = False
    None_message = False
    if res_unm > 5950:
        issuing_time_flag = True

    while True:
        total_page += 1
        time.sleep(1)
        print(f'当前总查询页码   :   {total_page}')
        if issuing_time_flag is True and None_message is False:
            if total_page == 120:
                # 按引用倒序
                return False, total_page, 1, count, False

            elif total_page == 240:
                # 按下载正序
                return False, total_page, 2, count, False

            elif total_page == 360:
                # 按引用正序
                return False, total_page, 3, count, False

            elif total_page == 480:
                return False, total_page, 4, count, False
                # 按下载倒序
            elif total_page == 600:
                # 按发表顺序倒
                return False, total_page, 5, count, False

            elif total_page == 720:
                # 按发表顺序倒
                return False, total_page, 6, count, False

            elif total_page == 840:
                # 按发表顺序倒
                return False, total_page, 7, count, False

            elif total_page == 960:
                flag333 = whit_file(date_str, paper_type, paper_day)
                if flag333 is True:
                    return True, False, -1, count, False

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 循环网页一页中的条目
        for i in range((count - 1) % paper_sum + 1, paper_sum + 1):
            # print(f"{res_unm} --- {count + len_data - new_paper_sum} --- {total_page}")
            if res_unm < count + len_data - new_paper_sum:
                logger.write_log("已获取完数据", 'info')
                flag333 = whit_file(date_str, paper_type, paper_day)
                if flag333 is True:
                    return True, False, -1, count, False

            if issuing_time_flag is False and total_page > res_unm / 50 + 1:
                logger.write_log("已获取完数据", 'info')
                flag333 = whit_file(date_str, paper_type, paper_day)
                if flag333 is True:
                    return True, False, -1, count, False

            print(f"正在爬取第{count + len_data - new_paper_sum}条基础数据,跳过{new_paper_sum}"
                  f"条(当前查询条件第{(count - 1) // paper_sum + 1}页第{i}条。总第{total_count + count}次查询 共{res_unm}条):")

            try:
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
                    err2(e)

                if '增强出版' in title:
                    title = title[:-5]

                if '网络首发' in title:
                    title = title[:-5]

                if_title = None
                for ii in paper_title:
                    if ii[0] == title:
                        print(f"数据已存在 : {title} \n")
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
                        f"(`UUID`, `title`, `receive_time`, `status`, `db_type`) "
                        f"VALUES ('{uuid}', '{title}', '{paper_day}', '0', '{db_type}');")

                sql3 = TrSQL(sql3)
                flag = Date_base().insert(sql3)
                if flag == '重复数据':
                    new_paper_sum += 1
                    logger.write_log(f"重复数据 ： {title}, UUID : {uuid}", 'info')
                    continue

                print(f"标题:    {title}")

                logger.write_log(f"已获取 ： {title}, UUID : {uuid} \n", 'info')

            except Exception as e:
                err2(e)
                if type(e).__name__ == 'TimeoutException' and issuing_time_flag is False:
                    print(f"{res_unm} ------- {count + len_data - new_paper_sum + 1}")
                    logger.write_log(f"已获取完数据 ，，{res_unm - (count + len_data - new_paper_sum + 1)}条数据无法获取",
                                     'info')
                    flag333 = whit_file(date_str, paper_type, paper_day)
                    if flag333 is True:
                        return True, False, -1, count, False

            finally:
                count += 1
            if res_unm <= count + len_data - new_paper_sum - 1:
                logger.write_log("已获取完数据 \n", 'info')
                flag333 = whit_file(date_str, paper_type, paper_day)

                if flag333 is True:
                    return True, False, -1, count, False
        time.sleep(1)
        try:
            ActionChains(driver).key_down(Keys.ARROW_RIGHT).key_up(Keys.ARROW_RIGHT).perform()
        finally:
            pass
        time.sleep(3)


def get_multi_title_data(driver, res_unm, time_out):
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    count = 0
    # 循环网页一页中的条目
    if res_unm <= 20:
        for_flag = 1
    else:
        for_flag = int(res_unm / 20) + 1

    print(res_unm)

    for a in range(for_flag):
        if a > 0:
            try:
                time.sleep(3)
                ActionChains(driver).key_down(Keys.ARROW_RIGHT).key_up(Keys.ARROW_RIGHT).perform()
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, "//a[@id='PageNext']"))).click()
            except Exception as e:
                err2(e)
        # title_list = None
        # title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        time.sleep(3)
        for i in range(20):
            count += 1

            print(f"正在爬取第{count}条基础数据,")

            title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{count}]/td[2]/a'''
            title_xpath2 = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{count}]/td[2]/div/div/a'''
            date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{count}]/td[5]'''
            ndb_type_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{count}]/td[6]/span'''

            try:
                title = WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, title_xpath))).text
            except:
                if count - 1 == res_unm:
                    return True
                else:
                    return False

            try:
                db_type = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.XPATH, ndb_type_xpath))).text
            except Exception as e:
                err3(e)
                db_type = None

            try:
                date = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.XPATH, date_xpath))).text
                if len(date) == 6:
                    date = f"{date[:4]}-{date[4:]}-01"
            except Exception as e:
                err3(e)
                date = None

            if db_type == '期刊':
                db_type = '1'
            elif db_type == '报纸':
                db_type = '0'
            elif db_type == '硕士':
                db_type = '2'
            elif db_type == '博士':
                db_type = '3'
            elif db_type == '图书':
                db_type = '4'
            elif db_type == '特色期刊':
                db_type = '5'
            elif db_type == '刊辑':
                db_type = '6'
            elif db_type == '中国会议':
                db_type = 'a'
            elif db_type == '国际会议':
                db_type = 'b'
            elif db_type == '国家标准':
                db_type = 'c'
            elif db_type == '国家标准':
                db_type = 'd'
            else:
                db_type = '9'

            title = title.replace(':', '：').replace('——', '—')

            if "<font color='red'>" in title:
                title = title.replace("<font color='red'>", "")

            title = title.replace("'", r"\'")
            uuid = UUID()
            sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                    f"(`UUID`, `title`, `receive_time`, `status`, `db_type`) "
                    f"VALUES ('{uuid}', '{title}', '{date}', '0', '{db_type}');")

            sql3 = TrSQL(sql3)
            flag = Date_base().insert(sql3)
            if flag == '重复数据':
                logger.write_log(f"重复数据 ： {title}, UUID : {uuid}", 'info')
                continue

            print(f"标题:    {title}")

            logger.write_log(f"已获取 ： {title}, UUID : {uuid} \n", 'info')
    return True
