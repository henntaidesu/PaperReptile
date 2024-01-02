import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from src.model.cnki import Crawl, positioned_element
from src.module.log import log
from src.module.read_conf import read_conf
from src.paper_website.cnki.cnki import get_mian_page_info
import random

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()


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
    driver.get(f"https://kns.cnki.net/kns8s/AdvSearch")
    random_sleep = round(random.uniform(0, 3), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)

    # 修改属性，使下拉框显示
    opt = driver.find_element(By.CSS_SELECTOR, open_page_data['pe'])  # 定位元素
    driver.execute_script(open_page_data['js'], opt)  # 执行 js 脚本进行属性的修改；arguments[0]代表第一个属性

    # # 传入关键字
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(
        keyword)
    #
    # 点击搜索
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()

    print("正在搜索，请稍后...")

    # 获取总文献数和页数
    res_unm = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['gn']))).text

    # 去除千分位里的逗号
    res_unm = int(res_unm.replace(",", ''))
    page_unm = int(res_unm / 20) + 1
    print(f"共找到 {res_unm} 条结果, {page_unm} 页。")
    return res_unm


def open_level2_page(driver, keyword):
    # 打开页面，等待两秒
    crossids = \
        f"YSTT4HG0%2CLSTPFY1C%2CJUP3MUPD%2CMPMFIG1A%2CWQ0UVIAA%2CBLZOG7CK%2CEMRPGLPA%2PARAGLIDING%2BILBO1Z6R%2CNN3FJMUV"
    driver.get(f"https://kns.cnki.net/kns8s/defaultresult/index?crossids={crossids}&korder=TI&kw={keyword}")
    random_sleep = round(random.uniform(2, 3), 2)
    print(f"sleep {random_sleep}s")
    time.sleep(random_sleep)

    # 修改属性，使下拉框显示
    opt = driver.find_element(By.CSS_SELECTOR, open_page_data['pe'])  # 定位元素
    driver.execute_script(open_page_data['js'], opt)  # 执行 js 脚本进行属性的修改；arguments[0]代表第一个属性

    # # 传入关键字
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['ik']))).send_keys(
        keyword)
    #
    # 点击搜索
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, open_page_data['cs']))).click()

    print("正在搜索，请稍后...")


def run_paper_main_info(paper_sum_flag):
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    driver = webserver(web_zoom)
    # 设置所需篇数
    open_page(driver, keyword)
    get_mian_page_info(driver, keyword, paper_sum_flag, time_out)
    driver.close()


def run_lever2_page(paper_sum_flag):
    web_zoom, keyword, papers_need, time_out = read_conf.cnki_paper()
    driver = webserver(web_zoom)
    # 设置所需篇数
    open_page(driver, keyword)
    get_mian_page_info(driver, keyword, paper_sum_flag, time_out)
    driver.close()
