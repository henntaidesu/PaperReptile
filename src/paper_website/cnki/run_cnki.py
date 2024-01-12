from selenium import webdriver
from src.model.cnki import Crawl, positioned_element, date_choose_start_table, date_choose_end_table
from src.module.read_conf import read_conf
from src.paper_website.cnki.get_cnki_message import get_paper_title, get_paper_info
from src.module.now_time import year, moon, day1
from src.paper_website.cnki.cnki_components import *
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()
dts = date_choose_start_table()
dte = date_choose_end_table()


def webserver(web_zoom):
    chromedriver_path = r"chromedriver.exe"
    # get直接返回，不再等待界面加载完成
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["pageLoadStrategy"] = "none"
    # 设置微软驱动器的环境
    options = webdriver.ChromeOptions()
    # 设置浏览器不加载图片，提高速度
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument(f"--force-device-scale-factor={web_zoom}")
    options.add_argument("--disable-gpu")
    # options.add_argument("--proxy-server=http://127.0.0.1:10809")
    service = ChromeService(chromedriver_path)
    # 指定chromedriver.exe的位置
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def setting_select_date(driver, time_out):
    try:
        cnki = CNKI()
        yy, mm, dd = cnki.read_cnki_date()
        now_yy = int(year())
        now_mm = int(moon())
        now_day = int(day1())

        paper_day = f"{yy}-{mm}-{dd}"

        flag_page = 0
        flag_yy = now_yy - yy
        flag_page += flag_yy * 12
        flag_mm = now_mm - mm
        flag_page += flag_mm
        # 设置开始时间
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox0'))).click()
        time.sleep(1)
        for i in range(flag_page):
            time.sleep(3)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located
                                                  ((By.XPATH, open_page_data['start_previous_page']))).click()

        time.sleep(1)

        date_list = str(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['start']))).text)[14:]
        date_list = date_list.splitlines()
        # 将每行的内容转化为整数列表
        date_list = [int(line) for line in date_list]
        list_flag = 0
        list_flag = date_list.index(1)

        while True:
            list_flag += 1
            if dd == date_list[list_flag - 1]:
                break

        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, dts[list_flag]))).click()

        time.sleep(3)

        # 设置结束时间
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.ID, 'datebox1'))).click()
        for i in range(flag_page):
            time.sleep(2)
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located
                                                  ((By.XPATH, open_page_data['end_previous_page']))).click()

        time.sleep(2)

        date_list = str(WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['end']))).text)[14:]
        date_list = date_list.splitlines()
        # 将每行的内容转化为整数列表
        date_list = [int(line) for line in date_list]
        list_flag = 0
        list_flag = date_list.index(1)
        while True:
            list_flag += 1
            if dd == date_list[list_flag - 1]:
                break
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, dte[list_flag]))).click()
        time.sleep(2)

        return paper_day
    except Exception as e:
        err(e)


def choose_banner(driver, time_out, paper_day):
    sql = f"select flag from cnki_page_flag WHERE date = '{paper_day}'"
    flag, data = Date_base().select_all(sql)
    if data:
        date_temp = data[0][0]
        data = data[0][0]
        if data == '1111111111':
            # logger.write_log(f'今日已获取{data}')
            revise_cnki_date()
            driver.close()
            run_get_paper_title()
        # print(data)
        data = list(data)
        # print(data)

        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['all_item']))).click()
        time.sleep(3)

        for i in range(9):
            if data[i] == '0':
                # 点击学术期刊
                WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.XPATH, open_page_data[i]))).click()
                return i, date_temp

    else:
        # 判断是否有数据
        xx_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['xx_sum']))).text
        xw_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['xw_sum']))).text
        hy_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['hy_sum']))).text
        pa_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['pa_sum']))).text
        ts_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['ts_sum']))).text
        bz_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['bz_sum']))).text
        cg_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['cg_sum']))).text
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['all_item']))).click()
        time.sleep(2)
        kj_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['kj_sum']))).text
        tsqk_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['tsqk_sum']))).text
        sp_sum = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['sp_sum']))).text

        if '万' in xx_sum:
            xx_sum = int(f"{xx_sum[:-1].replace('.', '')}00")
        else:
            xx_sum = int(xx_sum)
        if xx_sum > 0:
            a0 = '0'
        else:
            a0 = '1'

        if '万' in xw_sum:
            xw_sum = int(f"{xw_sum[:-1].replace('.', '')}00")
        else:
            xw_sum = int(xw_sum)
        if xw_sum > 0:
            a1 = '0'
        else:
            a1 = '1'

        if '万' in hy_sum:
            hy_sum = int(f"{hy_sum[:-1].replace('.', '')}00")
        else:
            hy_sum = int(hy_sum)
        if hy_sum > 0:
            a2 = '0'
        else:
            a2 = '1'

        if '万' in pa_sum:
            pa_sum = int(f"{pa_sum[:-1].replace('.', '')}00")
        else:
            pa_sum = int(pa_sum)
        if pa_sum > 0:
            a3 = '0'
        else:
            a3 = '1'

        if '万' in ts_sum:
            ts_sum = int(f"{ts_sum[:-1].replace('.', '')}00")
        else:
            ts_sum = int(ts_sum)
        if ts_sum > 0:
            a5 = '0'
        else:
            a5 = '1'

        if '万' in bz_sum:
            bz_sum = int(f"{bz_sum[:-1].replace('.', '')}00")
        else:
            bz_sum = int(bz_sum)
        if bz_sum > 0:
            a7 = '0'
        else:
            a7 = '1'

        if '万' in cg_sum:
            cg_sum = int(f"{cg_sum[:-1].replace('.', '')}00")
        else:
            cg_sum = int(cg_sum)
        if cg_sum > 0:
            a8 = '0'
        else:
            a8 = '1'

        if '万' in kj_sum:
            kj_sum = int(f"{kj_sum[:-1].replace('.', '')}00")
        else:
            kj_sum = int(kj_sum)
        if kj_sum > 0:
            a9 = '0'
        else:
            a9 = '1'

        if '万' in tsqk_sum:
            tsqk_sum = int(f"{tsqk_sum[:-1].replace('.', '')}00")
        else:
            tsqk_sum = int(tsqk_sum)
        if tsqk_sum > 0:
            a10 = '0'
        else:
            a10 = '1'

        if '万' in sp_sum:
            sp_sum = int(f"{sp_sum[:-1].replace('.', '')}00")
        else:
            sp_sum = int(sp_sum)
        if sp_sum > 0:
            a11 = '0'
        else:
            a11 = '1'

        item_flag = f"{a0}{a1}{a2}{a3}{a5}{a7}{a8}{a9}{a10}{a11}"
        print(item_flag)

        sql = (f"INSERT INTO `Paper`.`cnki_page_flag`(`date`, `flag`) VALUES "
               f"('{paper_day}', '{item_flag}');")

        sql = (f"INSERT INTO `Paper`.`cnki_page_flag`"
               f"(`date`, `flag`, `xxkq`, `xwlw`, `hy`, `bz`, `ts`, `bs`, `cg`, `xxkj`, `tsqk`, `sp`) "
               f"VALUES ('{paper_day}', '{item_flag}', '{xx_sum}', '{xw_sum}', '{hy_sum}', '{pa_sum}', '{ts_sum}', "
               f"'{bz_sum}', '{cg_sum}', '{kj_sum}', '{tsqk_sum}', '{sp_sum}');").replace("'0'", "NULL")

        Date_base().insert_all(sql)
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data[0]))).click()
        return 0, item_flag


def open_page(driver, keyword):
    # 打开页面，等待两秒
    try:
        url = f"https://kns.cnki.net/kns8/AdvSearch"
        # driver.add_cookie(cookie)
        driver.get(url)
        random_sleep = round(random.uniform(0, 3), 2)
        print(f"sleep {random_sleep}s")
        time.sleep(random_sleep)
        time_out = 10
        # os.system("pause")

        # 传入关键字
        # WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(keyword)

        # 设置时间
        paper_day = setting_select_date(driver, time_out)

        # 点击搜索
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()
        time.sleep(2)

        # 切换搜索文章类型
        paper_type, date_str = choose_banner(driver, time_out, paper_day)
        time.sleep(5)

        # 文献数和页数
        res_unm = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

        res_unm = int(res_unm.replace(",", ''))
        if res_unm > 5950:
            # 按发表顺序正
            WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
            time.sleep(2)
        if res_unm > 49:
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['display']))).click()
            time.sleep(2)
            WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.XPATH, open_page_data['50']))).click()
            time.sleep(2)

        paper_sum = 50

        # 去除千分位里的逗号

        page_unm = int(res_unm / paper_sum) + 1
        print(f"共找到 {res_unm} 条结果, {page_unm} 页。")
        return res_unm, paper_type, paper_day, date_str, paper_sum
    except Exception as e:
        err(e)


def open_paper_info(driver, keyword):
    time_out = 5
    driver.get("https://kns.cnki.net/kns8/AdvSearch")
    random_sleep = round(random.uniform(1, 2), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)

    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(
        keyword)

    WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()
    time.sleep(2)

    res_unm = WebDriverWait(driver, time_out).until(
        EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

    paper_sum = 20
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / paper_sum) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")

    return res_unm


def page_click_sort_type():
    pass


def run_get_paper_title():
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    try:
        driver = webserver(web_zoom)
        # 设置所需篇数
        yy, mm, dd = CNKI().read_cnki_date()
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        date = f"{yy}-{mm}-{dd}"

        page_flag = 0
        count = 1
        count_sum = 0
        flag, page_flag, click_flag, count = get_paper_title(driver, keyword, time_out, res_unm, date, paper_type,
                                                             paper_day, date_str, paper_sum, page_flag, count,
                                                             count_sum)

        if flag is True:
            driver.close()
            run_get_paper_title()

        driver.close()
        driver = webserver(web_zoom)
        time.sleep(3)
        count_sum = count
        count = 1
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="PT"]'))).click()
        flag, page_flag, click_flag, count = get_paper_title(driver, keyword, time_out, res_unm, date, paper_type,
                                                             paper_day, date_str, paper_sum, page_flag, count,
                                                             count_sum)

        if flag is True:
            driver.close()
            run_get_paper_title()

        driver.close()
        driver = webserver(web_zoom)
        time.sleep(3)
        count_sum = count * 2
        count -= 5950
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="CF"]'))).click()
        flag, page_flag, click_flag, count = get_paper_title(driver, keyword, time_out, res_unm, date, paper_type,
                                                             paper_day, date_str, paper_sum, page_flag, count,
                                                             count_sum)

        if flag is True:
            driver.close()
            run_get_paper_title()

        driver.close()
        driver = webserver(web_zoom)
        time.sleep(3)
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="CF"]'))).click()
        time.sleep(3)
        count_sum = count * 3
        count -= 5950
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="CF"]'))).click()
        flag, page_flag, click_flag, count = get_paper_title(driver, keyword, time_out, res_unm, date, paper_type,
                                                             paper_day, date_str, paper_sum, page_flag, count,
                                                             count_sum)

        if flag is True:
            driver.close()
            run_get_paper_title()

        driver.close()
        driver = webserver(web_zoom)
        time.sleep(3)
        count_sum = count * 4
        count -= 5950
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        flag, page_flag, click_flag, count = get_paper_title(driver, keyword, time_out, res_unm, date, paper_type,
                                                             paper_day, date_str, paper_sum, page_flag, count,
                                                             count_sum)

        if flag is True:
            driver.close()
            run_get_paper_title()

        driver.close()
        driver = webserver(web_zoom)
        time.sleep(3)
        res_unm, paper_type, paper_day, date_str, paper_sum = open_page(driver, keyword)
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        time.sleep(3)
        count_sum = count * 5
        count -= 5950
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="DFR"]'))).click()
        flag, page_flag, click_flag, count = get_paper_title(driver, keyword, time_out, res_unm, date, paper_type,
                                                             paper_day, date_str, paper_sum, page_flag, count,
                                                             count_sum)

        if flag is True:
            driver.close()
            run_get_paper_title()

    except Exception as e:
        err(e)

    # driver.close()


def run_get_paper_info(date):
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    driver = webserver(web_zoom)

    for i in date:
        uuid = i[0]
        title = i[1]
        receive_time = i[2]
        start = i[3]
        db_type = i[4]

        res_unm = open_paper_info(driver, title)
        get_paper_info(driver, time_out, uuid, title, db_type)

    # driver.close()
