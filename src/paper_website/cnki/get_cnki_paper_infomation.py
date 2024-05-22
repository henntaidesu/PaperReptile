from src.paper_website.cnki.cnki_components import *
import time
import re
import gc
import concurrent.futures
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.module.now_time import now_time
from src.model.cnki import Crawl, positioned_element, crawl_xpath, reference_papers, QuotePaper
from src.module.log import Log, err2, err3
from src.module.read_conf import ReadConf
from src.module.rabbitMQ import rabbitmq_produce

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = Log()
read_conf = ReadConf()


def get_paper_info(driver, time_out, uuid, title1, db_type, receive_time):
    try:
        new_title = None

        cp = crawl_xpath()
        rp = reference_papers()
        qp = QuotePaper()

        count = 1
        xpath_information = crawl_xp.xpath_inf()
        # new_paper_sum = 0
        title_list = WebDriverWait(driver, time_out).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        gc.collect()

        # title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[2]'''
        # authors_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[3]'''
        # source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[4]/p/a'''
        # date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[5]'''
        # ndb_type_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[6]/span'''
        # quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[7]/div/a'''
        # down_sun_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[8]/div/a'''

        title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[2]'''
        author_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[3]'''
        source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[4]'''
        date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[5]'''
        database_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[6]'''
        quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[7]'''
        download_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr/td[8]'''
        xpaths = [title_xpath, author_xpath, source_xpath, date_xpath, database_xpath, quote_xpath, download_xpath]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
        title, authors, source, date, ndb_type, quote, down_sun = [future.result() for future in future_elements]

        authors = str(authors).replace(r"'", r"\'")
        source = source.replace(r"'", r"\'")

        if quote is None or quote == '':
            quote = None
        if down_sun is None or down_sun == '':
            down_sun = None

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
        elif ndb_type == '科技成果':
            ndb_type = 'e'
        else:
            ndb_type = '9'
    except Exception as e:
        err3(e)
        return False

    # print(f"\n"
    #       f"标题:    {title}\n"
    #       f"作者:    {authors}\n"
    #       f"文章来源: {source}\n"
    #       f"数据来源: {db_flag}\n"
    #       f"引用次数: {quote}\n"
    #       f"下载次数: {down_sun}")

    try:
        title_list[0].click()  # 点击条目
        n = driver.window_handles  # 获取driver的句柄
        driver.switch_to.window(n[-1])  # driver切换至最新生产的页面
        time.sleep(3)
        if len(driver.window_handles) > 2:
            return False

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # 拉取页面到最低端
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
        try:
            institute = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                (By.XPATH, cp['institute']))).text
            if '.' in institute:
                institute = re.sub(r'\d*\.', ';', institute)[1:].replace(' ', '')
            institute = institute.replace("'", r"\'")
        except Exception as e:
            err3(e)
            institute = None
        # print(f"作者单位 : {institute}")

        # 获取摘要
        try:
            abstract = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['abstract']))).text
            abstract = abstract.replace("'", "\'")
        except Exception as e:
            err3(e)
            abstract = None
            driver.refresh()
        # print(f"摘要 : {abstract}")

        # 获取关键词
        try:
            classification_zh = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['keywords']))).text[:-1]
            classification_zh = Trim_passkey(classification_zh).replace('  ', ';').replace("'", r"\'")
        except Exception as e:
            err3(e)
            classification_zh = None

        # print(f"关键词 : {classification_zh}")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # 拉取页面到最低端
        class_list = get_choose_info(driver)
        class_dict = {}
        for item in class_list:
            class_dict[item[0]] = item[1]

        publication = class_dict.get('专辑：')
        topic = class_dict.get('专题：')
        DOI = class_dict.get('DOI：')
        classification_number = class_dict.get('分类号：')
        version_Number = class_dict.get('版号：')
        edition_name = class_dict.get('版名：')

        advisor = None
        subject = None
        if ndb_type in ('2', '3'):
            from src.paper_website.cnki.cnki_components import get_advisor_info
            class_list = get_advisor_info(driver)

            class_dict = {}
            for item in class_list:
                class_dict[item[0]] = item[1]

            advisor = class_dict.get('导师：')
            subject = class_dict.get('学科专业：')

            # electronic_journal_xpath = f'''//*[@id="bsdzqkcbxx"]/p'''
            # try:
            #     electronic_journal = WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, electronic_journal_xpath))).text
            # except:
            electronic_journal = None

        if len(driver.window_handles) > 2:
            return False

        if classification_number is None and version_Number is not None:
            classification_number = version_Number + edition_name

        # print(f"专辑 - {publication}")
        # print(f"专题 - {topic}")
        # print(f"分类号 - {classification_number}")
        # print(f"DOI - {DOI}")

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 获取资金资助
        try:
            funding = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['funds']))).text
            funding = funding.replace(' ', '').replace('；', ';').replace("'", "\'")
        except Exception as e:
            err3(e)
            funding = None
        # print(f"资金资助 : {funding}")

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
        # print(f"论文大小 : {paper_size}k")

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
        # print(f"论文页数 : {page_sum}")

        # 获取层级
        level = None
        if '报' in db_type or '报纸' in db_type:
            try:
                level = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp['level']))).text.replace("'", r"\'")
                # paper_size = int(paper_size[3:][:-1])
            except Exception as e:
                err3(e)
                level = None
        # print(f"报纸层级 : {level}")

        # 拉取页面到最低端
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 判断是否有参考文献
        rn = qp.reference_name()
        pl_list = qp.paper_list()
        journal_reference = None
        try:
            if_journal_reference = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                (By.XPATH, cp['if_literature_reference']))).text
            if if_journal_reference:
                # print("存在引文网络")
                pass

        except Exception as e:
            err3(e)
            if_journal_reference = None
            # print("该论文无引用文章")

        # if_journal_reference = None
        if if_journal_reference == '引文网络':
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # 拉取页面到最低端
            el = WebDriverWait(driver, time_out).until(EC.element_to_be_clickable((By.XPATH, cp['references'])))
            el.click()
            paper_flag = 0

            while True:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)  # 拉取页面到最低端
                time.sleep(1)
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
                    # print(f"存在引用{rn[paper_flag]} {paper_sum} 篇")
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
                        # print(f"[{iii[1:]}")
                        pass

                paper_list = trim_quote(paper_list)
                pl_list[paper_flag] = paper_list
                paper_flag += 1

        # print("获取文章目录")
        try:
            article_directory = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.CLASS_NAME, cp['catalog']))).text

            article_directory = article_directory.replace("'", r"\'")
            # print(f"文章目录 : \n{article_directory}")
        except Exception as e:
            err3(e)
            article_directory = None
            # print(f"文章目录 : {article_directory}")

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
            new_title = new_title.replace("'", r"\'")
        except Exception as e:
            err3(e)
            new_title = None
        # print(f"内页标题 : {new_title}")

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
                f"`Chinese_and_foreign`, `newpaper`, `patent`, `standard`, `advisor`, `subject`) "
                f"VALUES "
                f"('{uuid}', '{institute}', '{source}', '{ndb_type}', {down_sun}, {quote}, '{insert_time}',"
                f" '{update_time}', '{funding}', '{publication}', '{classification_number}',"
                f" '{article_directory}', '{topic}', '{level}', '{page_sum}', '{pl_list[0]}',"
                f" '{pl_list[1]}', '{pl_list[2]}', '{pl_list[3]}', '{pl_list[4]}',"
                f" '{pl_list[5]}', '{pl_list[6]}', '{pl_list[7]}', '{pl_list[8]}', '{advisor}', '{subject}');")

        sql3 = (f"UPDATE `Paper`.`cnki_index` SET "
                f"`receive_time` = '{date}', "
                f"`status` = '1', "
                f"`db_type` = '{ndb_type}' "
                f"WHERE `UUID` = '{uuid}';")

        sql1 = TrSQL(sql1)
        sql2 = TrSQL(sql2)
        sql3 = TrSQL(sql3)

        rabbitmq_produce('MYSQL_INSERT', sql1)
        rabbitmq_produce('MYSQL_INSERT', sql2)
        rabbitmq_produce('MYSQL_UPDATE', sql3)

        logger.write_log(f"已获取 ： {new_title}, UUID : {uuid}", 'info')
        return True

    except Exception as e:
        if type(e).__name__ in ('ElementClickInterceptedException', 'TimeoutException'):
            logger.write_log(f"元素获取错误 ： {title}, UUID : {uuid}", 'error')
        else:
            err2(e)

        return False
