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


def webserver(web_zoom):
    # get直接返回，不再等待界面加载完成
    desired_capabilities = DesiredCapabilities.EDGE
    desired_capabilities["pageLoadStrategy"] = "none"
    # 设置微软驱动器的环境
    options = webdriver.EdgeOptions()
    # 设置浏览器不加载图片，提高速度
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument(f"--force-device-scale-factor={web_zoom}")
    # 创建一个微软驱动器
    driver = webdriver.Edge(options=options)

    return driver


def open_page(driver, keyword):
    # 打开页面，等待两秒
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    random_sleep = round(random.uniform(0, 3), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)

    # 修改属性，使下拉框显示
    opt = driver.find_element(By.CSS_SELECTOR, open_page_data['pe'])  # 定位元素
    driver.execute_script(open_page_data['js'], opt)  # 执行 js 脚本进行属性的修改；arguments[0]代表第一个属性

    # 鼠标移动到下拉框中的[通讯作者]
    ActionChains(driver).move_to_element(driver.find_element(By.CSS_SELECTOR, open_page_data['ca'])).perform()

    # # 找到[关键词]选项并点击
    # WebDriverWait(driver, 100).until(
    #     EC.visibility_of_element_located((By.CSS_SELECTOR, 'li[data-val="KY"]'))).click()

    # 传入关键字
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(
        keyword)

    # 点击搜索
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()

    print("正在搜索，请稍后...")

    # # 点击切换中文文献
    # WebDriverWait(driver, 100).until(
    #     EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/a[1]"))
    # ).click()

    # 获取总文献数和页数
    res_unm = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

    # 去除千分位里的逗号
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / 20) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")
    return res_unm


def get_info(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text
    except:
        return '无'


def get_choose_info(driver, xpath1, xpath2, str):
    try:
        if WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath1))).text == str:
            return WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xpath2))).text
        else:
            return None
    except:
        return None


def crawl(driver, papers_need, keyword):
    global pl_list
    number = None
    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()

    count = 1
    xpath_information = crawl_xp.xpath_inf()

    sql = f"select title from `cnki_index` where `from` = '{keyword}'"
    flag, paper_title = Date_base().select_all(sql)

    for i in range((count - 1) // 20):
        # 切换到下一页
        random_sleep = round(random.uniform(0, 3), 2)
        print(f"sleep {random_sleep}s")
        time.sleep(random_sleep)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, cp['get_next_page']))).click()

    print(f"从第 {count} 条开始爬取\n")

    # 当爬取数量小于需求时，循环网页页码
    while count <= papers_need:
        # 等待加载完全，休眠3S
        time.sleep(3)

        title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        # 循环网页一页中的条目
        for i in range((count - 1) % 20 + 1, 21):
            if_title = False
            journal_list = None
            master_list = None
            PhD_list = None
            international_journals_list = None
            book_list = None
            Chinese_and_foreign_list = None

            print(
                f"\n#################正在爬取第 {count} 条(第{(count - 1) // 20 + 1}页第{i}条)##########################\n")

            try:
                term = (count - 1) % 20 + 1  # 本页的第几个条目
                xpaths = crawl_xp.xpath_base(term)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                title, authors, source, date, db_type, quote, down_sun = [future.result() for future in
                                                                          future_elements]

                for ii in paper_title:
                    if ii[0] == title:
                        print(f"数据已存在 : {title}")
                        if_title = True
                        break

                if if_title is True:
                    continue

                if not quote.isdigit():
                    quote = '0'
                if not down_sun.isdigit():
                    down_sun = '0'

                print(f"作者 ：{authors}\n"
                      f"来源 : {source}\n"
                      f"数据库： {db_type}\n"
                      f"引用次数：{quote}\n"
                      f"下载次数：{down_sun}")

                # 点击条目
                title_list[i - 1].click()

                # 获取driver的句柄
                n = driver.window_handles

                # driver切换至最新生产的页面
                driver.switch_to.window(n[-1])
                time.sleep(3)

                # 拉取页面到最低端
                # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

                # 开始获取页面信息
                # 点击展开
                try:
                    WebDriverWait(driver, 0).until(
                        EC.presence_of_element_located((By.XPATH, cp['WebDriverWait']))
                    ).click()
                except:
                    pass

                # 获取作者单位
                # print('正在获取作者单位')
                try:
                    institute = WebDriverWait(driver, 0).until(EC.presence_of_element_located(
                        (By.XPATH, cp['institute']))).text
                    if '.' in institute:
                        institute = re.sub(r'\d*\.', ';', institute)[1:].replace(' ', '')
                except:
                    institute = None
                print(f"作者单位 : {institute}")

                # print('正在获取摘要')
                try:
                    abstract = WebDriverWait(driver, 0).until(
                        EC.presence_of_element_located((By.CLASS_NAME, cp['abstract']))).text
                except:
                    abstract = None
                print(f"摘要 : {abstract}")

                # 获取关键词
                # print('获取关键词')
                try:
                    classification_zh = WebDriverWait(driver, 0).until(
                        EC.presence_of_element_located((By.CLASS_NAME, cp['keywords']))).text[:-1]
                except:
                    classification_zh = None
                    print("无法获取关键词")
                    sys.exit()
                classification_zh = Trim_passkey(classification_zh).replace('  ', ';')
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
                if topic is None:
                    logger.write_log(f"获取专题错误 ： {title}")
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
                if DOI is None:
                    logger.write_log(f"DOI ： {title}")
                print(f"DOI: {DOI}")

                # 获取资金资助
                # print('获取资金资助')
                try:
                    funding = WebDriverWait(driver, 0).until(
                        EC.presence_of_element_located((By.CLASS_NAME, cp['funds']))).text
                    funding = funding.replace(' ', '').replace('；', ';')
                except:
                    funding = None
                print(f"资金资助 : {funding}")

                # print('获取论文大小')
                paper_size_flag = 0
                while True:
                    paper_size_flag += 1
                    paper_size = WebDriverWait(driver, 0).until(EC.presence_of_element_located(
                        (By.XPATH, cp[f'paper_size{paper_size_flag}']))).text
                    if '大小' in paper_size:
                        paper_size = int(paper_size[3:][:-1])
                        break
                    if paper_size_flag > 8:
                        paper_size = None
                        break
                print(f"论文大小 : {paper_size}k")

                level = None
                if '报' in db_type or '报纸' in db_type:
                    try:
                        level = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                            (By.XPATH, cp['level']))).text
                        # paper_size = int(paper_size[3:][:-1])
                    except:
                        level = None
                print(f"报纸层级 : {level}")

                # 拉取页面到最低端
                # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

                # 判断是否有参考文献
                journal_reference = None
                try:
                    if_journal_reference = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                        (By.XPATH, cp['if_literature_reference']))).text
                    if if_journal_reference:
                        print("存在引文网络")

                except:
                    if_journal_reference = None
                    print("该论文无引用文章")

                if if_journal_reference == '引文网络':
                    el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, cp['references'])))
                    el.click()
                    paper_flag = 0

                    rn = qp.reference_name()
                    pl_list = qp.paper_list()

                    while True:
                        if paper_flag == len(pl_list):
                            break

                        continue_flag = False
                        # 期刊参考文件页数
                        try:
                            paper_sum = funding = WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                            paper_sum = int(paper_sum.find_element(By.ID, 'pc_JOURNAL').text)
                        except:
                            paper_sum = None
                            paper_flag += 1
                            continue_flag = True
                        if continue_flag is True:
                            try:
                                print(f"$$$本论文没有引用{rn[paper_flag]} Paper$$$")
                                pl_list[paper_flag] = None
                                continue
                            except:
                                break

                        if paper_sum:
                            print(f"存在{rn[paper_flag]}{paper_sum}篇")
                            journal_paper_sum = int((paper_sum / 10) + 1)
                            flag = 0
                            paper_list = []
                            while True:
                                funding = None
                                # 获取参考文献

                                funding = WebDriverWait(driver, 3).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                                li_elements = funding.find_elements(By.TAG_NAME, 'li')

                                for li in li_elements:
                                    li_text = li.text.replace('[', ';', 1)
                                    paper_list.append(li_text)

                                flag += 1
                                if flag > paper_sum:
                                    break

                                try:
                                    if_next_page = WebDriverWait(driver, 3).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                                    if_next_page = if_next_page.find_element(By.CLASS_NAME, 'next').text
                                except:
                                    break
                                if if_next_page == '下一页':
                                    el = WebDriverWait(driver, 3).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                                    el.find_element(By.CLASS_NAME, 'next').click()
                                    time.sleep(3)

                            for iii in paper_list:
                                print(f"引用期刊 :{iii}")

                        paper_list = trim_quote(paper_list)
                        pl_list[paper_flag] = paper_list
                        paper_flag += 1

                    # # 硕士论文
                    # try:
                    #     paper_sum = funding = WebDriverWait(driver, 3).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, rp['master'])))
                    #     paper_sum = int(paper_sum.find_element(By.ID, rp['paper_num']).text)
                    # except:
                    #     paper_sum = None
                    # if paper_sum:
                    #     print(f"存在引用硕士论文{paper_sum}篇")
                    #     paper_sum = int((paper_sum / 10) + 1)
                    #     if paper_sum > 1:
                    #         logger.write_log(f"发现硕士论文大于10 {title}")
                    #         sys.exit()
                    #     flag = 0
                    #     master_list = []
                    #     while True:
                    #         funding = None
                    #         # 获取参考文献
                    #
                    #         funding = WebDriverWait(driver, 3).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, rp['master'])))
                    #         li_elements = funding.find_elements(By.TAG_NAME, 'li')
                    #
                    #         for li in li_elements:
                    #             li_text = li.text.replace('[', ';', 1)
                    #             master_list.append(li_text)
                    #
                    #         flag += 1
                    #         if flag > paper_sum:
                    #             break
                    #
                    #         try:
                    #             if_next_page = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['master'])))
                    #             if_next_page = if_next_page.find_element(By.CLASS_NAME, rp['next_page']).text
                    #         except:
                    #             break
                    #         if if_next_page == '下一页':
                    #             el = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['master'])))
                    #             el.find_element(By.CLASS_NAME, rp['next_page']).click()
                    #             time.sleep(3)
                    #
                    #     master_list = sorted(set(master_list), key=extract_number)
                    #
                    #     for iii in master_list:
                    #         print(f"引用硕士论文 :{iii}")
                    #     master_list = trim_quote(master_list)
                    # else:
                    #     print("$$$本论文没有引用硕士论文$$$")
                    #
                    # # 博士论文
                    # try:
                    #     paper_sum = funding = WebDriverWait(driver, 3).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, rp['PhD'])))
                    #     paper_sum = int(paper_sum.find_element(By.ID, rp['paper_num']).text)
                    # except:
                    #     paper_sum = None
                    # if paper_sum:
                    #     print(f"存在引用博士论文{paper_sum}篇")
                    #     paper_sum = int((paper_sum / 10) + 1)
                    #     if paper_sum > 1:
                    #         logger.write_log(f"发现博士论文大于10 {title}")
                    #         sys.exit()
                    #     flag = 0
                    #     PhD_list = []
                    #     while True:
                    #         funding = None
                    #         # 获取参考文献
                    #
                    #         funding = WebDriverWait(driver, 3).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, rp['PhD'])))
                    #         li_elements = funding.find_elements(By.TAG_NAME, 'li')
                    #
                    #         for li in li_elements:
                    #             li_text = li.text.replace('[', ';', 1)
                    #             PhD_list.append(li_text)
                    #
                    #         flag += 1
                    #         if flag > paper_sum:
                    #             break
                    #
                    #         try:
                    #             if_next_page = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['PhD'])))
                    #             if_next_page = if_next_page.find_element(By.CLASS_NAME, rp['next_page']).text
                    #         except:
                    #             break
                    #         if if_next_page == '下一页':
                    #             el = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['PhD'])))
                    #             el.find_element(By.CLASS_NAME, rp['next_page']).click()
                    #             time.sleep(3)
                    #
                    #     PhD_list = sorted(set(PhD_list), key=extract_number)
                    #
                    #     for iii in PhD_list:
                    #         print(f"引用博士论文 :{iii}")
                    #
                    #     PhD_list = trim_quote(PhD_list)
                    #
                    # else:
                    #     print("$$$本论文没有引用博士论文$$$")
                    #
                    # # 国际期刊
                    # try:
                    #     paper_sum = funding = WebDriverWait(driver, 3).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, rp['international_journals'])))
                    #     paper_sum = int(paper_sum.find_element(By.ID, rp['paper_num']).text)
                    # except:
                    #     paper_sum = None
                    # if paper_sum:
                    #     print(f"存在引用国际期刊{paper_sum}篇")
                    #     paper_sum = int((paper_sum / 10) + 1)
                    #     if paper_sum > 1:
                    #         logger.write_log(f"发现国际期刊10 {title}")
                    #         sys.exit()
                    #     flag = 0
                    #     international_journals_list = []
                    #     while True:
                    #         funding = None
                    #         # 获取参考文献
                    #
                    #         funding = WebDriverWait(driver, 3).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, rp['international_journals'])))
                    #         li_elements = funding.find_elements(By.TAG_NAME, 'li')
                    #
                    #         for li in li_elements:
                    #             li_text = li.text.replace('[', ';', 1)
                    #             international_journals_list.append(li_text)
                    #
                    #         flag += 1
                    #         if flag > paper_sum:
                    #             break
                    #
                    #         try:
                    #             if_next_page = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['international_journals'])))
                    #             if_next_page = if_next_page.find_element(By.CLASS_NAME, rp['next_page']).text
                    #         except:
                    #             break
                    #         if if_next_page == '下一页':
                    #             el = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['international_journals'])))
                    #             el.find_element(By.CLASS_NAME, rp['next_page']).click()
                    #             time.sleep(3)
                    #
                    #     international_journals_list = sorted(set(international_journals_list), key=extract_number)
                    #
                    #     for iii in international_journals_list:
                    #         print(f"引用国际期刊 :{iii}")
                    #
                    #     international_journals_list = trim_quote(international_journals_list)
                    #
                    # else:
                    #     print("$$$本论文没有引用国际期刊$$$")
                    #
                    # # 图书
                    # try:
                    #     paper_sum = funding = WebDriverWait(driver, 3).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, rp['book'])))
                    #     paper_sum = int(paper_sum.find_element(By.ID, rp['paper_num']).text)
                    # except:
                    #     paper_sum = None
                    # if paper_sum:
                    #     print(f"存在引用图书{paper_sum}篇")
                    #     paper_sum = int((paper_sum / 10) + 1)
                    #     if paper_sum > 1:
                    #         logger.write_log(f"发现图书大于10 {title}")
                    #         sys.exit()
                    #     flag = 0
                    #     book_list = []
                    #     while True:
                    #         funding = None
                    #         # 获取参考文献
                    #
                    #         funding = WebDriverWait(driver, 3).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, rp['book'])))
                    #         li_elements = funding.find_elements(By.TAG_NAME, 'li')
                    #
                    #         for li in li_elements:
                    #             li_text = li.text.replace('[', ';', 1)
                    #             book_list.append(li_text)
                    #
                    #         flag += 1
                    #         if flag > paper_sum:
                    #             break
                    #
                    #         try:
                    #             if_next_page = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['book'])))
                    #             if_next_page = if_next_page.find_element(By.CLASS_NAME, rp['next_page']).text
                    #         except:
                    #             break
                    #         if if_next_page == '下一页':
                    #             el = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['book'])))
                    #             el.find_element(By.CLASS_NAME, rp['next_page']).click()
                    #             time.sleep(3)
                    #
                    #     book_list = sorted(set(book_list), key=extract_number)
                    #
                    #     for iii in book_list:
                    #         print(f"引用图书 :{iii}")
                    #
                    #     book_list = trim_quote(book_list)
                    #
                    # else:
                    #     print("$$$本论文没有引用图书$$$")
                    #
                    # # 中外文题录
                    # try:
                    #     paper_sum = funding = WebDriverWait(driver, 3).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, rp['Chinese_and_foreign'])))
                    #     paper_sum = int(paper_sum.find_element(By.ID, rp['paper_num']).text)
                    # except:
                    #     paper_sum = None
                    # if paper_sum:
                    #     print(f"存在引用中外文题录{paper_sum}篇")
                    #     paper_sum = int((paper_sum / 10) + 1)
                    #     if paper_sum > 1:
                    #         logger.write_log(f"发现中外文题录大于10 {title}")
                    #         sys.exit()
                    #     flag = 0
                    #     Chinese_and_foreign_list = []
                    #     while True:
                    #         funding = None
                    #         # 获取参考文献
                    #
                    #         funding = WebDriverWait(driver, 3).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, rp['Chinese_and_foreign'])))
                    #         li_elements = funding.find_elements(By.TAG_NAME, 'li')
                    #
                    #         for li in li_elements:
                    #             li_text = li.text.replace('[', ';', 1)
                    #             Chinese_and_foreign_list.append(li_text)
                    #
                    #         flag += 1
                    #         if flag > paper_sum:
                    #             break
                    #
                    #         try:
                    #             if_next_page = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['Chinese_and_foreign'])))
                    #             if_next_page = if_next_page.find_element(By.CLASS_NAME, rp['next_page']).text
                    #         except:
                    #             break
                    #         if if_next_page == '下一页':
                    #             el = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['Chinese_and_foreign'])))
                    #             el.find_element(By.CLASS_NAME, rp['next_page']).click()
                    #             time.sleep(3)
                    #
                    #     Chinese_and_foreign_list = sorted(set(Chinese_and_foreign_list), key=extract_number)
                    #
                    #     for iii in Chinese_and_foreign_list:
                    #         print(f"引用中外文题录 :{iii}")
                    #
                    #     Chinese_and_foreign_list = trim_quote(Chinese_and_foreign_list)
                    #
                    # else:
                    #     print("$$$本论文没有引用中外文题录$$$")
                    #
                    # # 中外文题录
                    # try:
                    #     paper_sum = funding = WebDriverWait(driver, 3).until(
                    #         EC.presence_of_element_located((By.CLASS_NAME, rp['Chinese_and_foreign'])))
                    #     paper_sum = int(paper_sum.find_element(By.ID, rp['paper_num']).text)
                    # except:
                    #     paper_sum = None
                    # if paper_sum:
                    #     print(f"存在引用中外文题录{paper_sum}篇")
                    #     paper_sum = int((paper_sum / 10) + 1)
                    #     if paper_sum > 1:
                    #         logger.write_log(f"发现中外文题录大于10 {title}")
                    #         sys.exit()
                    #     flag = 0
                    #     newpaper_list = []
                    #     while True:
                    #         funding = None
                    #         # 获取参考文献
                    #
                    #         funding = WebDriverWait(driver, 3).until(
                    #             EC.presence_of_element_located((By.CLASS_NAME, rp['newpaper'])))
                    #         li_elements = funding.find_elements(By.TAG_NAME, 'li')
                    #
                    #         for li in li_elements:
                    #             li_text = li.text.replace('[', ';', 1)
                    #             newpaper_list.append(li_text)
                    #
                    #         flag += 1
                    #         if flag > paper_sum:
                    #             break
                    #
                    #         try:
                    #             if_next_page = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['newpaper'])))
                    #             if_next_page = if_next_page.find_element(By.CLASS_NAME, rp['next_page']).text
                    #         except:
                    #             break
                    #         if if_next_page == '下一页':
                    #             el = WebDriverWait(driver, 3).until(
                    #                 EC.presence_of_element_located((By.CLASS_NAME, rp['newpaper'])))
                    #             el.find_element(By.CLASS_NAME, rp['next_page']).click()
                    #             time.sleep(3)
                    #
                    #     newpaper_list = sorted(set(newpaper_list), key=extract_number)
                    #
                    #     for iii in newpaper_list:
                    #         print(f"引用中外文题录 :{iii}")
                    #
                    #     newpaper_list = trim_quote(newpaper_list)
                    #
                    # else:
                    #     print("$$$本论文没有引用中外文题录$$$")
                    #     newpaper_list = None

                # 获取文章目录
                # print("获取文章目录")
                try:
                    article_directory = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, cp['catalog']))).text
                except:
                    article_directory = None
                print(f"文章目录 : \n{article_directory}")

                # print("获取报纸层级")

                url = driver.current_url[46:][:-32]

                # 获取下载链接
                # try:
                #     down_url = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located
                #                                               ((By.CLASS_NAME, "btn-dlpdf")))[0].get_attribute('href')
                #     down_url = urljoin(driver.current_url, down_url)
                # except:
                #     down_url = None

                # print("获取内页标题")
                try:
                    new_title = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h1"))
                    )
                    new_title = new_title.text
                except:
                    new_title = None
                print(f"内页标题 : {new_title}")

                uuid = UUID()
                insert_time = now_time()

                title_en = None
                classification_en = None
                update_time = None

                sql1 = (
                    f"INSERT INTO `Paper`.`index_copy1`(`UUID`, `web_site_id`, `classification_en`,`classification_zh`,"
                    f"`source_language`, `title_zh`, `title_en`, `update_time`, `insert_time`, `from`, `state`, "
                    f"`authors`, `Introduction`, `receive_time`, `Journal_reference`, `Comments`, `size`, `DOI`, "
                    f"`version`, `withdrawn`) "
                    f" VALUES ('{uuid}', '{uuid}', '{classification_en}', '{classification_zh}', "
                    f" 'cn', '{new_title}', '{title_en}', '{update_time}', '{insert_time}', 'cnki', '00', "
                    f" '{authors}', NULL, '{date}', NULL, NULL, {paper_size}, '{DOI}', NULL, NULL);")

                sql2 = (f"INSERT INTO `Paper`.`cnki_paper_information`"
                        f"(`UUID`, `institute`, `paper_from`, `db_type`, `down_sun`, `quote`, `insert_time`, "
                        f"`update_time`, `funding`, `album`, `classification_number`, "
                        f"`article_directory`, `Topics`, `level`, `journal_reference`, `journal`, "
                        f"`master`, `PhD`, `international_journals`, `book`, "
                        f"`Chinese_and_foreign`, 'newpaper') "
                        f"VALUES "
                        f"('{uuid}', '{institute}', '{source}', '{db_type}',' {down_sun}', '{quote}', '{insert_time}',"
                        f" '{update_time}', '{funding}', '{publication}', '{classification_number}',"
                        f" '{article_directory}', '{topic}', '{level}', '{journal_reference}', '{pl_list[0]}',"
                        f" '{pl_list[1]}', '{pl_list[2]}', '{pl_list[3]}', '{pl_list[4]}',"
                        f" '{pl_list[5]}', '{pl_list[6]}');")

                sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                        f"(`UUID`, `source_language`, `title`, `insert_time`, `from`) "
                        f"VALUES ('{uuid}', 'cn', '{title}', '{insert_time}', '{keyword}');")

                sql1 = TrSQL(sql1)
                sql2 = TrSQL(sql2)
                sql3 = TrSQL(sql3)

                # Date_base().insert_all(sql1)
                # Date_base().insert_all(sql2)
                # Date_base().insert_all(sql3)

                logger.write_log(f"已获取 ： {new_title}, UUID : {uuid}")
                random_sleep = round(random.uniform(0, 3), 2)
                print(f"sleep {random_sleep}s")
                time.sleep(1000000000)

            except:
                logger.write_log(f"错误 ： {new_title}, UUID : {uuid}")
                continue

            finally:
                # 如果有多个窗口，关闭第二个窗口， 切换回主页
                n2 = driver.window_handles
                if len(n2) > 1:
                    driver.close()
                    driver.switch_to.window(n2[0])
                # 计数,判断需求是否足够
                count += 1
                if count == papers_need: break

        # 切换到下一页
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, cp['paper_next_page']))).click()


def cnki_run():
    web_zoom, keyword, papers_need = read_conf.cnki_paper()
    driver = webserver(web_zoom)
    # 设置所需篇数
    res_unm = open_page(driver, keyword)
    # 判断所需是否大于总篇数
    papers_need = papers_need if (papers_need <= res_unm) else res_unm
    # os.system("pause")
    # 开始爬取
    crawl(driver, papers_need, keyword)
    # 关闭浏览器
    driver.close()
