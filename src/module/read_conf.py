import pymysql
import configparser


class ReadConf:
    config = None

    def __init__(self):
        # 如果配置信息尚未加载，则加载配置文件
        if not ReadConf.config:
            ReadConf.config = self._load_config()

    def _load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')
        return self.config

    def database(self):
        host = self.config.get('database', 'host')
        port = int(self.config.get('database', 'port'))
        user = self.config.get('database', 'user')
        password = self.config.get('database', 'password')
        database = self.config.get('database', 'database')
        db = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        return db

    def http_proxy(self):
        if_true = self.config.get('http_proxy', 'status')
        host = self.config.get('http_proxy', 'host')
        port = self.config.get('http_proxy', 'port')
        proxy_url = "http://" + host + ":" + port

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        # print(type(if_true))
        if if_true == "True":
            return True, proxies
        else:
            return False, proxies

    def socks5(self):
        host = self.config.get('socks5_proxy', 'host')
        port = self.config.get('socks5_proxy', 'port')
        proxy_url = f"socks5://{host}:{port}"
        return proxy_url

    def baidu_api(self):
        baidu_rapid = self.config.get('baidu_translate', 'rapid')
        key = self.config.get('baidu_translate', 'key')
        return baidu_rapid, key

    def log_level(self):
        level = self.config.get('LogLevel', 'level')
        return level

    def ChatGPT(self):
        key = self.config.get('ChatGPT', 'key')
        model = self.config.get('ChatGPT', 'model')
        base_url = self.config.get('ChatGPT', 'base_url')
        prompt = self.config.get('ChatGPT', 'prompt')
        return key, model, base_url, prompt

    def processes(self):
        number = int(self.config.get('processes', 'number'))
        start_sleep = int(self.config.get('processes', 'state_sleep'))
        return number, start_sleep

    def down_path(self):
        path = self.config.get('Paper_Down_Path', 'path')
        # if '\\' in path:
        #     path = path.replace('\\','\\\\')
        return path

    def cnki_proxy(self):
        status = self.config.get('cnki_proxy', 'status')
        # print(type(if_true))
        if status == "True":
            return True
        else:
            return False

    def elasticsearch(self):
        host = self.config.get('elasticsearch', 'host')
        ES_URL = f'http://{host}:9200'
        return ES_URL


class ArxivYYMM:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')

    def read_arxiv_yy_mm_code(self):
        yy_mm = self.config.get('arxiv.org', 'yy_mm')
        code = self.config.get('arxiv.org', 'code')
        return yy_mm, code

    def write_arxiv_yy_mm_code(self, yy_mm, code):
        self.config.set('arxiv.org', 'yy_mm', yy_mm)
        self.config.set('arxiv.org', 'code', code)
        with open('conf.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)


class CNKI:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')

    def read_cnki_date(self):
        year = int(self.config.get('cnki date', 'year'))
        moon = int(self.config.get('cnki date', 'moon'))
        day = int(self.config.get('cnki date', 'day'))
        return year, moon, day

    def write_cnki_date(self, year, moon, day):
        self.config.set('cnki date', 'year', year)
        self.config.set('cnki date', 'moon', moon)
        self.config.set('cnki date', 'day', day)
        with open('conf.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
