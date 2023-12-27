def xpath_inf():
    xpaths = [
        # 专辑
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[1]/p"),
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[2]/p"),
        # 专题
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[1]/p"),
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[2]/p"),
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[4]/ul/li[1]/p"),
        # 分类号
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/p"),
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[7]/ul/li[3]/p"),
        ("/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/span", "/html/body/div[2]/div[1]/div[3]/div/div/div[6]/ul/li[3]/p"),
    ]

    return xpaths


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
