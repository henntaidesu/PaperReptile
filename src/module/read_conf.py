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

    def cnki_proxy(self):
        true = self.config.get('Paper File Path', 'true')
        host = self.config.get('Paper File Path', 'host')
        port = self.config.get('Paper File Path', 'port')
        proxy_url = "http://" + host + ":" + port

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        # print(type(if_true))
        if true == "True":
            return True, proxies
        else:
            return False, proxies

    def cnki_paper(self):
        web_zoom = self.config.get('cnki paper passkey', 'web_zoom')
        keyword = self.config.get('cnki paper passkey', 'keyword')
        papers_need = int(self.config.get('cnki paper passkey', 'papers_need'))
        time_out = int(self.config.get('cnki paper passkey', 'time_out'))
        return web_zoom, keyword, papers_need, time_out

    def cnki_skip_db(self):
        newpaper = self.config.get('cnki skip jump', '报纸')
        journal = self.config.get('cnki skip jump', '期刊')
        journal_A = self.config.get('cnki skip jump', '特色期刊')
        master = self.config.get('cnki skip jump', '硕士')
        PhD = self.config.get('cnki skip jump', '博士')

        if newpaper == "True":
            newpaper = True
        else:
            newpaper = False

        if journal == "True":
            journal = True
        else:
            journal = False

        if journal_A == "True":
            journal_A = True
        else:
            journal_A = False

        if master == "True":
            master = True
        else:
            master = False

        if PhD == "True":
            PhD = True
        else:
            PhD = False

        return [newpaper, journal, master, PhD]


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

