def positioned_element():  # 定位元素
    xpaths = {
        'pe': '''div.sort-list''',
        'js': "arguments[0].setAttribute('style', 'display: block;')",
        'ca': 'li[data-val="RP"]',
        'ik': '''//*[@id="gradetxt"]/dd[1]/div[2]/input''',
        'cs': '''//*[@id="ModuleSearch"]/div[1]/div/div[2]/div/div[1]/div[1]/div[2]/div[3]/input''',
        'gn': '''//*[@id="countPageDiv"]/span[1]/em''',
    }

    return xpaths


def crawl_xpath():
    xpaths = {
        'abstract': "abstract-text",
        'keywords': "keywords",
        'funds': "funds",
        'catalog': "catalog",
        'get_next_page': '''//*[@id='PageNext']''',
        'WebDriverWait': '''//*[@id="ChDivSummaryMore"]''',
        'paper_size': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[4]''',
        'institute': "/html/body/div[2]/div[1]/div[3]/div/div/div[3]/div/h3[2]",
        'paper_next_page': "//a[@id='PageNext']",
    }
    return xpaths


class Crawl:

    @staticmethod
    def xpath_inf():
        xpaths = [
            # 专辑
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
            # 专题
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/p"),
            # 分类号
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[4]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[4]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[4]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[4]/p"),
            # 版名
            ("/html/body/div[2]/div[1]/div[3]/div[1]/div/div[5]/span",
             "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[5]/p"),
            # 版号
            ("/html/body/div[2]/div[1]/div[3]/div[1]/div/div[6]/span",
             "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[6]/p"),
        ]

        return xpaths

    @staticmethod
    def xpath_base(term):
        title_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[2]'''
        author_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[3]'''
        source_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[4]'''
        date_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[5]'''
        database_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[6]'''
        quote_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[7]'''
        download_xpath = f'''//*[@id="gridTable"]/div/div/table/tbody/tr[{term}]/td[8]'''

        xpaths = [title_xpath, author_xpath, source_xpath, date_xpath, database_xpath, quote_xpath,
                  download_xpath]
        return xpaths
