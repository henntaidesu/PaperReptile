def keyword():
    a = '人工智能'
    L = [a]
    return L


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
        'catalog': "catalog-list",
        'get_next_page': '''//*[@id='PageNext']''',
        'WebDriverWait': '''//*[@id="ChDivSummaryMore"]''',
        'institute': "/html/body/div[2]/div[1]/div[3]/div/div/div[3]/div/h3[2]",
        'paper_next_page': "//a[@id='PageNext']",
        'level': '//*[@id="func610"]/div/span',
        'references': '//*[@id="references"]',
        'literature_if_true': '//*[@id="refpartdiv"]/h5/span/b',
        'if_literature_reference': '//*[@id="refpartdiv"]/h5/span/b',
        'paper_size1': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[1]''',
        'paper_size2': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[2]''',
        'paper_size3': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[3]''',
        'paper_size4': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[4]''',
        'paper_size5': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[5]''',
        'paper_size6': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[6]''',
        'paper_size7': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[7]''',
        'paper_size8': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[8]''',
        'paper_size9': '''//*[@id="DownLoadParts"]/div[2]/div/div/p/span[9]''',
    }

    return xpaths


def reference_papers():
    xpaths = {
        # 通用
        'next_page': 'next',
        'paper_num': 'pc_JOURNAL',
        # 期刊
        'journal': 'quotation-journal',
        # 硕士论文
        'master': 'quotation-dissertation-m',
        # 博士论文
        'PhD': 'quotation-dissertation-d',
        # 国际期刊
        'international_journals': 'quotation-journal-w',
        # 图书
        'book': 'quotation-book',
        # 中外文题录
        'Chinese_and_foreign': 'quotation-crldeng',
        # 报纸
        'newpaper': 'quotation-newpaper',
    }

    return xpaths


class QuotePaper:
    @staticmethod
    def reference_name():
        journa = 'journal'
        master = 'master'
        PhD = 'PhD'
        international_journals = 'international_journals'
        book = 'book'
        Chinese_and_foreign = 'Chinese_and_foreign'
        newpaper = 'newpaper'
        paper = [journa, master, PhD, international_journals, book, Chinese_and_foreign, newpaper]
        return paper

    @staticmethod
    def paper_list():
        journal = None
        master = None
        PhD = None
        international = None
        book = None
        Chinese_and_foreign = None
        newpaper = None
        paper = [journal, master, PhD, international, book, Chinese_and_foreign, newpaper]
        return paper


class Crawl:

    @staticmethod
    def xpath_inf():
        xpaths = [
            # 专辑
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[3]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[3]/p"),
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
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[4]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[5]/ul/li[4]/p"),
            # 版名
            ("/html/body/div[2]/div[1]/div[3]/div[1]/div/div[5]/span",
             "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[5]/p"),
            # 版号
            ("/html/body/div[2]/div[1]/div[3]/div[1]/div/div[6]/span",
             "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[6]/p"),
            # DOI
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/p"),
            # list
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/p"),
            ("/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[2]/span",
             "/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[2]/p"),

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
