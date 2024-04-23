import http.client
import hashlib
import sys
import urllib
import random
import json
from src.module.read_conf import ReadConf
from src.module.log import Log, err2
from pygtrans import Translate


class translate:

    def __init__(self):
        self.conf = ReadConf()
        self.logger = Log()

    def baiduTR(self, language, to_language, text):

        httpClient = None
        baidu_rapid, key = self.conf.baidu_api()
        url = '/api/trans/vip/translate'
        salt = random.randint(32768, 65536)
        sign = baidu_rapid + text + str(salt) + key
        sign = hashlib.md5(sign.encode()).hexdigest()
        url = (url + '?appid=' + baidu_rapid + '&q=' + urllib.parse.quote(text) +
               '&from=' + language + '&to=' + to_language + '&salt=' + str(salt) + '&sign=' + sign)

        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', url)
            # response是HTTPResponse对象
            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            err_code = str(result['error_code'])
            if err_code == "54000":
                dst_content = str(result['trans_result'][0]['dst'])
                return dst_content

            else:
                error_msg = str(result['error_msg'])
                self.logger.write_log(f"{err_code} , {error_msg}")
                sys.exit()

        except Exception as e:
            self.logger.logger.write_log(f"An error occurred: {str(e)}")

        finally:
            if httpClient:
                httpClient.close()

    def GoogleTR(self, text, to_language):
        try:
            proxy = self.conf.socks5()
            client = Translate(target=to_language, proxies={'https': proxy}, domain='com')
            trans_text = client.translate(text).translatedText
            return trans_text
        except Exception as e:
            err2(e)
