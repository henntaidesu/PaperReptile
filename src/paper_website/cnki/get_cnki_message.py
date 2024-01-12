from src.paper_website.cnki.cnki_components import *
from src.module.read_conf import read_conf

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()


def get_paper_title(driver, keyword, time_out, res_unm, date, paper_type, paper_day, date_str, paper_sum, page_flag,
                    count, count_sum):
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
    xpath_information = crawl_xp.xpath_inf()
    dt = None
    if paper_type == 0:
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `xxkq` = {res_unm} WHERE `date` ='{date}';"
        dt = "'1'"
    elif paper_type == 1:
        dt = "'2', '3'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `xwlw` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 2:
        dt = "'c'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `hy` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 3:
        dt = "'0'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `bz` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 4:
        dt = "'4'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `ts` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 5:
        dt = "'a'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `bs` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 6:
        dt = "'b'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `cg` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 7:
        dt = "'6'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `xxkj` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 8:
        dt = "'5'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `tsqk` = {res_unm} WHERE `date` = '{date}';"
    elif paper_type == 9:
        dt = "'7'"
        sql = f"UPDATE `Paper`.`cnki_page_flag` SET `sp` = {res_unm} WHERE `date` = '{date}';"
    Date_base().update_all(sql)

    sql = (f"SELECT title FROM cnki_index where receive_time >= "
           f"'{date} 00:00:00' and receive_time <= '{date} 23:59:59' and db_type in ({dt})")
    flag, paper_title = Date_base().select_all(sql)

    len_data = len(paper_title)

    issuing_time_flag = False
    quote1_flag = False
    quote2_flag = False
    down1_flag = False
    down2_flag = False
    return_flag = False
    if res_unm > 5950:
        issuing_time_flag = True

    # 当爬取数量小于需求时，循环网页页码
    while True:
        page_flag += 1
        if issuing_time_flag is True:
            if page_flag == 120:
                # 按引用倒序
                return False, page_flag, 1, count

            if page_flag == 240:
                # 按下载正序
                return False, page_flag, 2, count

            if page_flag == 360:
                # 按引用正序
                return False, page_flag, 3, count

            if page_flag == 480:
                return False, page_flag, 4, count
                # 按下载倒序
            if page_flag == 600:
                # 按发表顺序倒
                return False, page_flag, 5, count

            if page_flag == 720:
                flag333 = whit_file(date_str, paper_type, paper_day)
                if flag333 is True:
                    return True, False, -1, count

        # 等待加载完全，休眠1S
        time.sleep(1)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        # 循环网页一页中的条目
        for i in range((count - 1) % paper_sum + 1, paper_sum + 1):
            print(f"{res_unm} ------- {count + len_data - new_paper_sum}")
            if res_unm < count + len_data - new_paper_sum:
                logger.write_log("已获取完数据")

                flag333 = whit_file(date_str, paper_type, paper_day)

                if flag333 is True:
                    return True, False, -1, count
            print(f"正在爬取第{count + len_data - new_paper_sum}条基础数据,跳过{new_paper_sum}"
                  f"条(第{(count - 1) // paper_sum + 1}页第{i}条 总第{count_sum + count}次查询 共{res_unm}条):")

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
                    if title == '抱歉，暂无数据，请稍后重试。' and issuing_time_flag is True and page_flag % 120 != 0:
                        return False, False, 1, count

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
                        f"VALUES ('{uuid}', '{title}', '{date}', '0', '{db_type}');")

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
                        return True, False, -1, count

            finally:
                count += 1
            continue_flag = False
            if res_unm <= count + len_data - new_paper_sum - 1:
                logger.write_log("已获取完数据")

                flag333 = whit_file(date_str, paper_type, paper_day)

                if flag333 is True:
                    return True, False, -1, count
            # time.sleep(1)

        try:
            time.sleep(3)
            ActionChains(driver).key_down(Keys.ARROW_RIGHT).key_up(Keys.ARROW_RIGHT).perform()
        except Exception as e:
            err(e)


def get_paper_info(driver, time_out, uuid, title1, db_type):
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

    for i in range((count - 1) % 20 + 1, 21):

        term = (count - 1) % 20 + 1  # 本页的第几个条目
        count += 1

        xpaths = crawl_xp.xpath_base(term)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
        title, authors, source, date, ndb_type, quote, down_sun = [future.result() for future in future_elements]

        if not quote.isdigit():
            quote = '0'
        if not down_sun.isdigit():
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

        sql3_flag = False
        if title == title1:
            sql3_flag = True

        if sql3_flag is False:
            uuid1 = UUID()
            sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                    f"(`UUID`, `title`, `receive_time`, `start`, `db_type`) "
                    f"VALUES ('{uuid1}', '{title}', '{date}', '1', '{ndb_type}');")
            sql3 = TrSQL(sql3)
            flag = Date_base().insert_all(sql3)
            if flag == '重复数据':
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
            term = (count - 1) % 20 + 1  # 本页的第几个条目
            xpaths = crawl_xp.xpath_base(term)

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
                        except Exception as e:
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
            Date_base().insert_all(sql1)
            Date_base().insert_all(sql2)
            Date_base().update_all(sql3)

            all_handles = driver.window_handles

            # 关闭除第一个窗口以外的所有窗口
            if len(all_handles) > 1:
                pass

            for handle in all_handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
                driver.switch_to.window(all_handles[0])

            logger.write_log(f"已获取 ： {new_title}, UUID : {uuid}")
            # return True

        except Exception as e:
            logger.write_log(f"错误 ： {new_title}, UUID : {uuid}")
            err(e)
