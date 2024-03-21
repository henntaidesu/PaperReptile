from src.paper_website.cnki.cnki_components import *
import time
import re
import gc
import concurrent.futures
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.module.execution_db import Date_base
from src.module.UUID import UUID
from src.module.now_time import now_time
from src.model.cnki import Crawl, positioned_element, crawl_xpath, reference_papers, QuotePaper
from src.module.log import Log, err2, err3
from src.module.read_conf import read_conf


open_page_data = positioned_element()
crawl_xp = Crawl()
logger = Log()
read_conf = read_conf()


def get_paper_info(driver, time_out, uuid, title1, db_type, receive_time):
    new_title = None

    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()

    count = 1
    xpath_information = crawl_xp.xpath_inf()

    # new_paper_sum = 0

    time.sleep(2)

    title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
    # 循环网页一页中的条目
    if len(title_list) > 1:
        sql = f"UPDATE `cnki_index` SET `start` = 'a' WHERE `UUID` = '{uuid}';"
        Date_base().update(sql)
        driver.close()
        return 'a'

    for i in range(19):

        gc.collect()

        if i == len(title_list):
            driver.close()
            return True

        # term = (count - 1) % 20 + 1  # 本页的第几个条目
        count += 1
        if len(title_list) == 1:
            title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[2]/a'''
            authors_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[3]/a'''
            source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[4]/p/a'''
            date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[5]'''
            ndb_type_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[6]/span'''
            quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[7]/div/a'''
            down_sun_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[8]/div/a'''

        else:
            title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]/td[2]/a'''
            authors_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]/td[3]'''
            source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]/td[4]/p/a'''
            date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]/td[5]'''
            ndb_type_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]/td[6]/a/span'''
            quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]/td[7]/div/a'''
            down_sun_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{i + 1}]td[8]/div/a'''

        title = WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, title_xpath))).text
        try:
            authors = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, authors_xpath))).text
        except Exception as e:
            err3(e)
            authors = None

        try:
            source = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, source_xpath))).text
        except Exception as e:
            err3(e)
            source = None
        try:
            date = WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, date_xpath))).text
        except Exception as e:
            err3(e)
            date = None

        try:
            ndb_type = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, ndb_type_xpath))).text
        except Exception as e:
            err3(e)
            ndb_type = None
        try:
            quote = WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, quote_xpath))).text
        except Exception as e:
            err3(e)
            quote = '0'
        try:
            down_sun = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, down_sun_xpath))).text
        except Exception as e:
            err3(e)
            down_sun = '0'

        if '增强出版' in title:
            title = title[:-5]
        if '网络首发' in title:
            title = title[:-5]

        db_flag = ndb_type

        if ndb_type == '期刊':
            ndb_type = '1'
        elif ndb_type == '报纸':
            ndb_type = '0'
        elif ndb_type == '硕士':
            ndb_type = '2'
        elif ndb_type == '博士':
            ndb_type = '3'
        elif ndb_type == '图书':
            ndb_type = '4'
        elif ndb_type == '特色期刊':
            ndb_type = '5'
        elif ndb_type == '刊辑':
            ndb_type = '6'
        elif ndb_type == '中国会议':
            ndb_type = 'a'
        elif ndb_type == '国际会议':
            ndb_type = 'b'
        elif ndb_type == '国家标准':
            ndb_type = 'c'
        elif ndb_type == '国家标准':
            ndb_type = 'd'
        else:
            ndb_type = '9'

        if ":" in title:
            title = title.replace(':', '：')
        elif "：" in title:
            title = title.replace('：', ':')

        if ":" in title1:
            title1 = title1.replace(':', '：')
        elif "：" in title1:
            title1 = title1.replace('：', ':')

        if "<font color='red'>" in title:
            title = title.replace("<font color='red'>", "")

        if "——" in title:
            title = title.replace('——', '—')
        if "——" in title1:
            title1 = title1.replace('——', '—')

        # 判断是否重复数据
        duplicate_data = False
        if title == title1:
            duplicate_data = True
        elif len(title_list) == 1 and date == receive_time:
            duplicate_data = True

        if duplicate_data is False:
            uuid1 = UUID()
            title = TrimString(title)
            sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                    f"(`UUID`, `title`, `receive_time`, `start`, `db_type`) "
                    f"VALUES ('{uuid1}', '{title}', '{date}', '1', '{ndb_type}');")
            sql3 = TrSQL(sql3)
            flag = Date_base().insert(sql3)
            print(sql3)
            if flag == '重复数据':
                print("重复数据")
                sql3 = f"UPDATE `Paper`.`cnki_index` SET  `start` = '*' WHERE UUID = '{uuid}';"
                Date_base().update(sql3)
                continue
            else:
                uuid = uuid1

        print(f"\n"
              f"标题:    {title}\n"
              f"作者:    {authors}\n"
              f"文章来源: {source}\n"
              f"数据来源: {db_flag}\n"
              f"引用次数: {quote}\n"
              f"下载次数: {down_sun}")

        try:
            # term = (count - 1) % 20 + 1  # 本页的第几个条目
            # xpaths = crawl_xp.xpath_base(term)

            # 点击条目
            title_list[i - 1].click()

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
            except Exception as e:
                err3(e)
                pass

            # 获取作者单位
            # print('正在获取作者单位')
            try:
                institute = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp['institute']))).text
                if '.' in institute:
                    institute = re.sub(r'\d*\.', ';', institute)[1:].replace(' ', '')
            except Exception as e:
                err3(e)
                institute = None
            print(f"作者单位 : {institute}")

            # print('正在获取摘要')
            try:
                abstract = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['abstract']))).text
            except Exception as e:
                err3(e)
                abstract = None
                driver.refresh()
            print(f"摘要 : {abstract}")

            # 获取关键词
            # print('获取关键词')
            try:
                classification_zh = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['keywords']))).text[:-1]
                classification_zh = Trim_passkey(classification_zh).replace('  ', ';')
            except Exception as e:
                err3(e)
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
                logger.write_log(f"获取专辑错误 ： {title}", 'error')
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
                logger.write_log(f"获取分类号错误 ： {title}", 'error')
            print(f"分类号 : {classification_number}")

            # 获取DOI
            # print('获取DOI')
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, 'DOI：') for xpath1, xpath2 in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            DOI = next((result for result in results if result is not None), None)
            # if DOI is None:
            #     logger.write_log(f"DOI ： {title}", 'error')
            print(f"DOI: {DOI}")

            # 获取资金资助
            # print('获取资金资助')
            try:
                funding = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['funds']))).text
                funding = funding.replace(' ', '').replace('；', ';')
            except Exception as e:
                err3(e)
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

            # 获取层级
            level = None
            if '报' in db_type or '报纸' in db_type:
                try:
                    level = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                        (By.XPATH, cp['level']))).text
                    # paper_size = int(paper_size[3:][:-1])
                except Exception as e:
                    err3(e)
                    level = None
            print(f"报纸层级 : {level}")

            # 拉取页面到最低端
            # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

            # 判断是否有参考文献
            rn = qp.reference_name()
            pl_list = qp.paper_list()
            # journal_reference = None
            try:
                if_journal_reference = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp['if_literature_reference']))).text
                if if_journal_reference:
                    print("存在引文网络")

            except Exception as e:
                err3(e)
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
                    except Exception as e:
                        err3(e)
                        paper_sum = None
                        paper_flag += 1
                        continue_flag = True
                    if continue_flag is True:
                        try:
                            # print(f"$$$本论文没有引用{rn[paper_flag]} Paper$$$")
                            continue
                        except Exception as e:
                            err3(e)
                            break

                    if paper_sum:
                        print(f"存在引用{rn[paper_flag]} {paper_sum} 篇")
                        # journal_paper_sum = int((paper_sum / 10) + 1)
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
                            except Exception as e:
                                err3(e)
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
            except Exception as e:
                err3(e)
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
            except Exception as e:
                err3(e)
                new_title = None
            print(f"内页标题 : {new_title}")

            insert_time = now_time()

            title_en = None
            classification_en = None
            update_time = now_time()

            sql1 = (
                f"INSERT INTO `Paper`.`index`(`UUID`, `web_site_id`, `classification_en`,`classification_zh`,"
                f"`source_language`, `title_zh`, `title_en`, `update_time`, `insert_time`, `from`, `state`, "
                f"`authors`, `Introduction`, `receive_time`, `Journal_reference`, `Comments`, `size`, `DOI`, "
                f"`version`, `withdrawn`) "
                f" VALUES ('{uuid}', '{uuid}', '{classification_en}', '{classification_zh}', "
                f" 'cn', '{new_title}', '{title_en}', '{update_time}', '{insert_time}', 'cnki', '00', "
                f" '{authors}', NULL, '{date}', NULL, NULL, {paper_size}, '{DOI}', NULL, NULL);")

            sql2 = (f"INSERT INTO `Paper`.`cnki_paper_information`"
                    f"(`UUID`, `institute`, `paper_from`, `db_type`, `down_sun`, `quote`, `insert_time`, "
                    f"`update_time`, `funding`, `album`, `classification_number`, "
                    f"`article_directory`, `Topics`, `level`, `page_sum`, `journal`, "
                    f"`master`, `PhD`, `international_journals`, `book`, "
                    f"`Chinese_and_foreign`, `newpaper`) "
                    f"VALUES "
                    f"('{uuid}', '{institute}', '{source}', '{db_type}',' {down_sun}', '{quote}', '{insert_time}',"
                    f" '{update_time}', '{funding}', '{publication}', '{classification_number}',"
                    f" '{article_directory}', '{topic}', '{level}', '{page_sum}', '{pl_list[0]}',"
                    f" '{pl_list[1]}', '{pl_list[2]}', '{pl_list[3]}', '{pl_list[4]}',"
                    f" '{pl_list[5]}', '{pl_list[6]}');")

            sql3 = (f"UPDATE `Paper`.`cnki_index` SET "
                    f"`receive_time` = '{date}', "
                    f"`start` = '1', "
                    f"`db_type` = '{ndb_type}' "
                    f"WHERE `UUID` = '{uuid}';")

            sql1 = TrSQL(sql1)
            sql2 = TrSQL(sql2)
            sql3 = TrSQL(sql3)

            try:
                Date_base().insert(sql1)
            finally:
                try:
                    Date_base().insert(sql2)
                finally:
                    Date_base().update(sql3)

            all_handles = driver.window_handles

            if len(all_handles) > 1:
                # 保留第一个句柄
                main_handle = all_handles[0]

                # 关闭除第一个页面外的所有页面
                for handle in all_handles[1:]:
                    driver.switch_to.window(handle)
                    driver.close()

                # 切换回第一个页面
                driver.switch_to.window(main_handle)

            logger.write_log(f"已获取 ： {new_title}, UUID : {uuid}", 'info')

        except Exception as e:
            logger.write_log(f"错误 ： {new_title}, UUID : {uuid}", 'error')
            err2(e)
