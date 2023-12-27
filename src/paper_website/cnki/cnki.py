import sys
import time
import concurrent.futures
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
import os
from src.module.execution_db import Date_base
from src.module.UUID import UUID
from src.module.now_time import now_time
from src.model.cnki import xpath_inf, xpath_base
from src.module.log import log

logger = log()


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


def TrSQL(sql):
    sql = sql.replace("None", "NULL").replace("'NULL'", "NULL")
    return sql


def webserver():
    # get直接返回，不再等待界面加载完成
    desired_capabilities = DesiredCapabilities.EDGE
    desired_capabilities["pageLoadStrategy"] = "none"

    # 设置微软驱动器的环境
    options = webdriver.EdgeOptions()
    # 设置浏览器不加载图片，提高速度
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    # 创建一个微软驱动器
    driver = webdriver.Edge(options=options)

    return driver


def open_page(driver, keyword):
    # 打开页面，等待两秒
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    time.sleep(2)

    # 修改属性，使下拉框显示
    opt = driver.find_element(By.CSS_SELECTOR, 'div.sort-list')  # 定位元素
    driver.execute_script("arguments[0].setAttribute('style', 'display: block;')",
                          opt)  # 执行 js 脚本进行属性的修改；arguments[0]代表第一个属性

    # 鼠标移动到下拉框中的[通讯作者]
    ActionChains(driver).move_to_element(driver.find_element(By.CSS_SELECTOR, 'li[data-val="RP"]')).perform()

    # # 找到[关键词]选项并点击
    # WebDriverWait(driver, 100).until(
    #     EC.visibility_of_element_located((By.CSS_SELECTOR, 'li[data-val="KY"]'))).click()

    # 传入关键字
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '''//*[@id="gradetxt"]/dd[1]/div[2]/input'''))
    ).send_keys(keyword)

    # 点击搜索
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located(
            (By.XPATH, '''//*[@id="ModuleSearch"]/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/div[3]/input'''))
    ).click()

    print("正在搜索，请稍后...")

    # # 点击切换中文文献
    # WebDriverWait(driver, 100).until(
    #     EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/a[1]"))
    # ).click()

    # 获取总文献数和页数
    res_unm = WebDriverWait(driver, 100).until(EC.presence_of_element_located(
        (By.XPATH, '''//*[@id="countPageDiv"]/span[1]/em'''))
    ).text

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
    count = 1
    xpath_information = xpath_inf()

    for i in range((count - 1) // 20):
        # 切换到下一页
        time.sleep(3)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='PageNext']"))).click()

    print(f"从第 {count} 条开始爬取\n")

    # 当爬取数量小于需求时，循环网页页码
    while count <= papers_need:
        # 等待加载完全，休眠3S
        time.sleep(3)

        title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        # 循环网页一页中的条目
        for i in range((count - 1) % 20 + 1, 21):
            print(
                f"\n###正在爬取第 {count} 条(第{(count - 1) // 20 + 1}页第{i}条)#######################################\n")

            try:
                term = (count - 1) % 20 + 1  # 本页的第几个条目
                xpaths = xpath_base(term)

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                title, authors, source, date, db_type, quote, down_sun = [future.result() for future in
                                                                          future_elements]

                # db = Date_base
                # sql = f"select `cnki_index`"
                # flag, paper_title = db.select_all(sql)

                if not quote.isdigit():
                    quote = '0'
                if not down_sun.isdigit():
                    down_sun = '0'

                # 点击条目
                title_list[i - 1].click()

                # 获取driver的句柄
                n = driver.window_handles

                # driver切换至最新生产的页面
                driver.switch_to.window(n[-1])
                time.sleep(3)

                # 开始获取页面信息
                # 点击展开
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, '''//*[@id="ChDivSummaryMore"]'''))
                    ).click()
                except:
                    pass

                # 获取作者单位
                print('正在获取institute...')
                try:
                    institute = WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[2]/div[1]/div[3]/div/div/div[3]/div/h3[2]"))).text
                except:
                    institute = None
                print(institute)

                # 获取摘要、关键词、专辑、专题
                # 获取摘要
                print('正在获取abstract...')
                try:
                    abstract = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "abstract-text"))).text
                except:
                    abstract = None
                # print(abstract + '\n')

                # 获取关键词
                # print('正在获取keywords...')
                try:
                    classification_zh = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "keywords"))).text[:-1]
                except:
                    classification_zh = None
                    print("无法获取TAG")
                    sys.exit()
                classification_zh = Trim_passkey(classification_zh)
                # print(classification_zh)

                # 获取专辑
                print('获取专辑')
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专辑：') for xpath1, xpath2 in
                               xpath_information]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                publication = next((result for result in results if result is not None), None)
                if publication is None:
                    logger.write_log(f"获取专辑错误 ： {title}")
                print(publication)

                # 获取专题
                print('获取专题')
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专题：') for xpath1, xpath2 in
                               xpath_information]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                topic = next((result for result in results if result is not None), None)
                if topic is None:
                    logger.write_log(f"获取专题错误 ： {title}")
                print(topic)

                # 获取分类号
                print('获取分类号')
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '分类号：') for xpath1, xpath2 in
                               xpath_information]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                classification_number = next((result for result in results if result is not None), None)
                if classification_number is None:
                    logger.write_log(f"获取分类号错误 ： {title}")
                print(classification_number)

                # 获取资金资助
                print('获取资金资助')
                try:
                    funding = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "funds"))).text
                except:
                    funding = None
                print(funding)

                print('获取论文大小')
                try:
                    paper_size = WebDriverWait(driver, 0).until(EC.presence_of_element_located(
                        (By.XPATH, '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[4]'''))).text
                    paper_size = int(paper_size[3:][:-1])
                except:
                    paper_size = None
                print(paper_size)

                # 获取文章目录
                try:
                    article_directory = WebDriverWait(driver, 0).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "catalog-list"))).text
                except:
                    article_directory = None
                print(article_directory)

                url = driver.current_url[46:][:-32]

                # 获取下载链接
                try:
                    down_url = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located
                                                          ((By.CLASS_NAME, "btn-dlpdf")))[0].get_attribute('href')
                    down_url = urljoin(driver.current_url, down_url)
                except:
                    down_url = None

                # 写入文件

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
                    f" VALUES ('{uuid}', '{url}', '{classification_en}', '{classification_zh}', "
                    f" 'cn', '{title}', '{title_en}', '{update_time}', '{insert_time}', 'cnki', '00', "
                    f" '{authors}', NULL, '{date}', NULL, NULL, {paper_size}, NULL, NULL, NULL);")

                sql2 = (f"INSERT INTO `Paper`.`cnki_paper_information`"
                        f"(`UUID`, `institute`, `paper_from`, `db_type`, `down_sun`, `quote`, `insert_time`, "
                        f"`update_time`, `funding`, `album`, `classification_number`, "
                        f"`article_directory`, `Topics`, `down_url`) "
                        f"VALUES "
                        f"('{uuid}', '{institute}', '{source}', '{db_type}',' {down_sun}', '{quote}', '{insert_time}',"
                        f" '{update_time}', '{funding}', '{publication}', '{classification_number}',"
                        f" '{article_directory}', '{topic}', '{down_url}');")

                sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                        f"(`UUID`, `source_language`, `title`, `insert_time`, `from`) "
                        f"VALUES ('{uuid}', cn, '{title}', '{insert_time}', '{keyword}');")

                sql1 = TrSQL(sql1)
                sql2 = TrSQL(sql2)
                sql3 = TrSQL(sql3)
                sql = [sql1, sql2, sql3]

                Date_base.insert_list(sql)

                logger.write_log(f"已获取 ： {title}")
                time.sleep(3)

            except:
                logger.write_log(f"失败 ： {title}")
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
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@id='PageNext']"))).click()


def cnki_run(keyword, papers_need):
    driver = webserver()
    # 设置所需篇数
    res_unm = open_page(driver, keyword)
    # 判断所需是否大于总篇数
    papers_need = papers_need if (papers_need <= res_unm) else res_unm
    # os.system("pause")
    # 开始爬取
    crawl(driver, papers_need, keyword)
    # 关闭浏览器
    driver.close()
