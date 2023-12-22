import pymysql
import configparser


class read_conf:
    config = None

    def __init__(self):
        # 如果配置信息尚未加载，则加载配置文件
        if not read_conf.config:
            read_conf.config = self._load_config()

    def _load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')
        return self.config

    def database(self):
        host = self.config.get('database', 'host')
        port = self.config.get('database', 'port')
        port = int(port)
        user = self.config.get('database', 'user')
        password = self.config.get('database', 'password')
        data_base = self.config.get('database', 'database')
        db = pymysql.connect(host=host, port=port, user=user, password=password, database=data_base)
        return db

    def http_proxy(self):
        if_true = self.config.get('http_proxy', 'true')
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
        host = self.config.get('socks5', 'host')
        port = self.config.get('socks5', 'port')
        proxy_url = f"socks5://{host}:{port}"
        return proxy_url

    def baidu_api(self):
        baidu_rapid = self.config.get('baidu translate', 'rapid')
        key = self.config.get('baidu translate', 'key')
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
        number = self.config.get('processes', 'number')
        return number

    def down_path(self):
        path = self.config.get('Paper File Path', 'path')
        # if '\\' in path:
        #     path = path.replace('\\','\\\\')
        return path


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
