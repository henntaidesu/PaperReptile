import sys
import time
import os
import re
import concurrent.futures
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from src.module.execution_db import Date_base
from src.module.UUID import UUID
from src.module.now_time import now_time
from src.model.cnki import Crawl, positioned_element, crawl_xpath, reference_papers, QuotePaper
from src.module.log import log
from src.module.read_conf import read_conf
from src.module.err_message import err
import random

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()


def TrimString(Str):
    if '\n' in Str:
        Str = Str.replace('\n', ' ')
    # if ' ' in Str:
    #     Str = Str.replace(' ', '')
    # if '/' in Str:
    #     Str = Str.replace('/', ' ')
    if "'" in Str:
        Str = Str.replace("'", "\\'")
    if '"' in Str:
        Str = Str.replace('"', '\\"')
    return Str


def Trim_passkey(Str):
    Str = Str.replace(";", " ")
    return Str


def trim_quote(Str):
    Str = str(Str)
    Str = Str.replace(',', '').replace("'", "").replace('] ', '、')
    Str = Str.replace(' ', '')[2:][:-1]
    return Str


def extract_number(item):
    match = re.search(r"(\d+)\]", item)
    return int(match.group(1)) if match else float('inf')


def TrSQL(sql):
    sql = sql.replace("None", "NULL").replace("'NULL'", "NULL")
    return sql


def get_info(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text
    except:
        return None


def get_choose_info(driver, xpath1, xpath2, str):
    try:
        if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath1))).text == str:
            return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath2))).text
        else:
            return None
    except:
        return None


def get_mian_page_info(driver, keyword, paper_sum_flag, time_out):
    paper_db = read_conf.cnki_skip_db()
    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()

    count = 1
    xpath_information = crawl_xp.xpath_inf()

    sql = f"select title from `cnki_index` where `from` = '{keyword}'"
    flag, paper_title = Date_base().select_all(sql)

    new_paper_sum = 0

    for i in range((count - 1) // 20):
        # 切换到下一页
        random_sleep = round(random.uniform(0, 3), 2)
        print(f"sleep {random_sleep}s")
        time.sleep(random_sleep)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, cp['get_next_page']))).click()

    print(f"从第 {count} 条开始爬取\n")

    # 当爬取数量小于需求时，循环网页页码
    while True:
        # 等待加载完全，休眠3S
        time.sleep(3)

        title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        # 循环网页一页中的条目
        for i in range((count - 1) % 20 + 1, 21):

            if count < paper_sum_flag:
                count += 1
                continue

            print(f"正在爬取第{count - new_paper_sum}条基础数据,跳过{new_paper_sum + paper_sum_flag}"
                  f"条(第{(count - 1) // 20 + 1}页第{i}条 总第{count}条):")

            try:
                term = (count - 1) % 20 + 1  # 本页的第几个条目
                xpaths = crawl_xp.xpath_base(term)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                title, authors, source, date, db_type, quote, down_sun = [future.result() for future in
                                                                          future_elements]

                url = None

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
                    continue

                uuid = UUID()
                sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                        f"(`UUID`, `title`, `receive_time`, `from`, `start`) "
                        f"VALUES ('{uuid}', '{title}', '{date}', '{keyword}', '0');")

                sql3 = TrSQL(sql3)
                flag = Date_base().insert_all(sql3)
                if flag == '重复数据':
                    logger.write_log(f"重复数据 ： {title}, UUID : {uuid}")
                    random_sleep = round(random.uniform(0, 3), 2)
                    print(f"sleep {random_sleep}s")
                    time.sleep(random_sleep)
                    continue

                if not quote.isdigit():
                    quote = '0'
                if not down_sun.isdigit():
                    down_sun = '0'

                print(f"\n"
                      f"作者:    {authors}\n"
                      f"文章来源: {source}\n"
                      f"数据来源: {db_type}\n"
                      f"引用次数: {quote}\n"
                      f"下载次数: {down_sun}")

                insert_time = now_time()

                sql1 = (f"INSERT INTO `Paper`.`index_copy1`(`UUID`, `web_site_id`,`source_language`, `title_zh`,"
                        f" `insert_time`, `from`, `state`, `authors`, `Introduction`, `receive_time`) "
                        f" VALUES ('{uuid}', '{uuid}', 'cn', '{title}', '{insert_time}', 'cnki', '00', "
                        f" '{authors}', NULL, '{date}');")

                sql2 = (f"INSERT INTO `Paper`.`cnki_paper_information`"
                        f"(`UUID`, `paper_from`, `db_type`, `down_sun`, `quote`, `insert_time`, `url`) "
                        f"VALUES "
                        f"('{uuid}', '{source}', '{db_type}',' {down_sun}', '{quote}', '{insert_time}', '{url}');")

                sql1 = TrSQL(sql1)
                sql2 = TrSQL(sql2)

                Date_base().insert_all(sql1)
                Date_base().insert_all(sql2)

                logger.write_log(f"已获取 ： {title}, UUID : {uuid}")

            except Exception as e:
                err(e)
                continue

            finally:
                count += 1

        time.sleep(3)
        # 切换到下一页
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, cp['paper_next_page']))).click()


def get_level2_page(driver, keyword, paper_sum_flag, time_out, uuid, title, db_type):
    paper_db = read_conf.cnki_skip_db()

    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()

    count = 1
    xpath_information = crawl_xp.xpath_inf()

    new_paper_sum = 0

    # 等待加载完全，休眠3S
    time.sleep(3)

    title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
    # 循环网页一页中的条目

    if count < paper_sum_flag:
        count += 1

    # if_title = False
    # journal_list = None
    # master_list = None
    # PhD_list = None
    # international_journals_list = None
    # book_list = None
    # Chinese_and_foreign_list = None
    # title = None
    # authors = None
    # source = None
    # date = None
    # db_type = None
    # quote = None
    # down_sun = None

    try:
        term = (count - 1) % 20 + 1  # 本页的第几个条目
        xpaths = crawl_xp.xpath_base(term)

        # 点击条目
        try:
            title_list[0].click()
        except Exception as e:
            driver.refresh()
            # count += 1
            err(e)

        # 获取driver的句柄
        n = driver.window_handles

        # driver切换至最新生产的页面
        driver.switch_to.window(n[-1])
        time.sleep(3)

        # 拉取页面到最低端
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 开始获取页面信息
        # 点击展开
        try:
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, cp['WebDriverWait']))
            ).click()
        except:
            pass

        # 获取作者单位
        # print('正在获取作者单位')
        try:
            institute = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                (By.XPATH, cp['institute']))).text
            if '.' in institute:
                institute = re.sub(r'\d*\.', ';', institute)[1:].replace(' ', '')
        except:
            institute = None
        print(f"作者单位 : {institute}")

        # print('正在获取摘要')
        try:
            abstract = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['abstract']))).text
        except:
            abstract = None
            driver.refresh()
        print(f"摘要 : {abstract}")

        # 获取关键词
        # print('获取关键词')
        try:
            classification_zh = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['keywords']))).text[:-1]
            classification_zh = Trim_passkey(classification_zh).replace('  ', ';')
        except:
            classification_zh = None
            # print("无法获取关键词")

        print(f"关键词 : {classification_zh}")

        # 获取专辑
        # print('获取专辑')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专辑：') for xpath1, xpath2 in
                       xpath_information]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        publication = next((result for result in results if result is not None), None)
        if publication is None:
            logger.write_log(f"获取专辑错误 ： {title}")
        print(f"专辑 : {publication}")

        # 获取专题
        # print('获取专题')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专题：') for xpath1, xpath2 in
                       xpath_information]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        topic = next((result for result in results if result is not None), None)
        print(f"专题 : {topic}")

        # 拉取页面到最低端
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 获取分类号 版名
        # print('获取分类号')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '分类号：') for xpath1, xpath2 in
                       xpath_information]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        classification_number = next((result for result in results if result is not None), None)
        if classification_number is None:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '版名：') for xpath1, xpath2
                           in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            classification_number = next((result for result in results if result is not None), None)
            # 获取版号
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '版号：') for xpath1, xpath2
                           in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            number = next((result for result in results if result is not None), None)
            if classification_number:
                classification_number = f"{classification_number}-{number}"
            else:
                classification_number = number
        if classification_number is None:
            logger.write_log(f"获取分类号错误 ： {title}")
        print(f"分类号 : {classification_number}")

        # 获取DOI
        # print('获取DOI')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, 'DOI：') for xpath1, xpath2 in
                       xpath_information]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        DOI = next((result for result in results if result is not None), None)
        # if DOI is None:
        #     logger.write_log(f"DOI ： {title}")
        print(f"DOI: {DOI}")

        # 获取资金资助
        # print('获取资金资助')
        try:
            funding = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['funds']))).text
            funding = funding.replace(' ', '').replace('；', ';')
        except:
            funding = None
        print(f"资金资助 : {funding}")

        # print('获取论文大小')
        paper_size_flag = 0
        while True:
            paper_size_flag += 1
            paper_size = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                (By.XPATH, cp[f'paper_size{paper_size_flag}']))).text
            if '大小' in paper_size:
                paper_size = int(paper_size[3:][:-1])
                break
            if paper_size_flag > 8:
                paper_size = None
                break
        print(f"论文大小 : {paper_size}k")

        # print('获取论文页数')
        paper_page_flag = 0
        while True:
            paper_page_flag += 1
            page_sum = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                (By.XPATH, cp[f'paper_size{paper_page_flag}']))).text
            if '页数' in page_sum:
                page_sum = int(page_sum[3:])
                break
            if paper_page_flag > 8:
                page_sum = None
                break
        print(f"论文页数 : {page_sum}")

        level = None
        if '报' in db_type or '报纸' in db_type:
            try:
                level = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp['level']))).text
                # paper_size = int(paper_size[3:][:-1])
            except:
                level = None
        print(f"报纸层级 : {level}")

        # 拉取页面到最低端
        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 判断是否有参考文献
        rn = qp.reference_name()
        pl_list = qp.paper_list()
        journal_reference = None
        try:
            if_journal_reference = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                (By.XPATH, cp['if_literature_reference']))).text
            if if_journal_reference:
                print("存在引文网络")

        except:
            if_journal_reference = None
            print("该论文无引用文章")

        # if_journal_reference = None
        if if_journal_reference == '引文网络':
            el = WebDriverWait(driver, time_out).until(EC.element_to_be_clickable((By.XPATH, cp['references'])))
            el.click()
            paper_flag = 0

            while True:
                if paper_flag == len(pl_list):
                    break
                paper_list = None
                continue_flag = False
                # 期刊参考文件页数
                try:
                    paper_sum = WebDriverWait(driver, time_out).until(
                        EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                    paper_sum = int(paper_sum.find_element(By.ID, 'pc_JOURNAL').text)
                except:
                    paper_sum = None
                    paper_flag += 1
                    continue_flag = True
                if continue_flag is True:
                    try:
                        # print(f"$$$本论文没有引用{rn[paper_flag]} Paper$$$")
                        continue
                    except:
                        break

                if paper_sum:
                    print(f"存在引用{rn[paper_flag]} {paper_sum} 篇")
                    journal_paper_sum = int((paper_sum / 10) + 1)
                    flag = 0
                    paper_list = []
                    while True:
                        # 获取参考文献

                        li_elements = WebDriverWait(driver, time_out).until(
                            EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                        li_elements = li_elements.find_elements(By.TAG_NAME, 'li')

                        for li in li_elements:
                            li_text = li.text.replace('[', ';', 1)
                            paper_list.append(li_text)

                        flag += 1
                        if flag > paper_sum:
                            break

                        try:
                            if_next_page = WebDriverWait(driver, time_out).until(
                                EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                            if_next_page = if_next_page.find_element(By.CLASS_NAME, 'next').text
                        except:
                            break
                        if if_next_page == '下一页':
                            el = WebDriverWait(driver, time_out).until(
                                EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                            # 滚动到元素可见位置
                            next_button = el.find_element(By.CLASS_NAME, 'next')
                            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                            # 然后点击元素
                            next_button.click()
                            time.sleep(3)

                    for iii in paper_list:
                        print(f"[{iii[1:]}")

                paper_list = trim_quote(paper_list)
                pl_list[paper_flag] = paper_list
                paper_flag += 1

        # print("获取文章目录")
        try:
            article_directory = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['catalog']))).text
            print(f"文章目录 : \n{article_directory}")
        except:
            article_directory = None
            print(f"文章目录 : {article_directory}")

        # url = driver.current_url[46:][:-32]
        # 获取下载链接
        # try:
        #     down_url = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located
        #                                               ((By.CLASS_NAME, "btn-dlpdf")))[0].get_attribute('href')
        #     down_url = urljoin(driver.current_url, down_url)
        # except:
        #     down_url = None

        # print("获取内页标题")
        try:
            new_title = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            new_title = new_title.text
        except:
            new_title = None
        print(f"内页标题 : {new_title}")

        insert_time = now_time()

        title_en = None
        classification_en = None
        update_time = now_time()

        sql1 = (f"UPDATE `Paper`.`index_copy1` SET  "
                f"`classification_zh` = '{classification_zh}', "
                f"`update_time` = '{update_time}', "
                f"`size` = {paper_size}, "
                f"`DOI` = '{DOI}', "
                f"WHERE `UUID` = '{uuid}';)")

        sql2 = (f"UPDATE `Paper`.`cnki_paper_information` SET "
                f"`institute` = '{institute}', "
                f"`update_time` = '{update_time}', "
                f"`funding` = '{funding}', "
                f"`album` = '{publication}', "
                f"`classification_number` = '{classification_number}', "
                f"`article_directory` = '{article_directory}', "
                f"`Topics` = '{topic}', "
                f"`level` = '{level}', "
                f"`page_sum` = '{page_sum}', "
                f"`journal` = '{pl_list[0]}', "
                f"`master` = '{pl_list[1]}', "
                f"`PhD` = '{pl_list[2]}', "
                f"`international_journals` = '{pl_list[3]}', "
                f"`book` = '{pl_list[4]}', "
                f"`Chinese_and_foreign` = '{pl_list[5]}', "
                f"`newpaper` = '{pl_list[6]}' "
                f"WHERE `UUID` = '{uuid}';")


        # sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
        #         f"(`UUID`, `title`, `receive_time`, `from`) "
        #         f"VALUES ('{uuid}', '{title}', '{date}', '{keyword}');")

        sql1 = TrSQL(sql1)
        sql2 = TrSQL(sql2)

        Date_base().insert_all(sql1)
        Date_base().insert_all(sql2)

        logger.write_log(f"已获取 ： {new_title}, UUID : {uuid}")
        random_sleep = round(random.uniform(0, 3), 2)
        print(f"sleep {random_sleep}s")
        time.sleep(random_sleep)


    except Exception as e:
        logger.write_log(f"错误 ： {new_title}, UUID : {uuid}")
        err(e)
