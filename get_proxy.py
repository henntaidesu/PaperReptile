from src.module.execution_db import Date_base
from src.module.now_time import proxy_time
from src.module.log import Log
from src.module.read_conf import ReadConf
import requests
import time


def proxy_pool():
    while True:
        sql = f"SELECT * FROM `proxy_pool` where `status` = '1' and expire_time > '{proxy_time()}' limit 100"
        # sql = f"SELECT * FROM `proxy_pool` where `status` = '1'  and expire_time < '{proxy_time()}' limit 100"
        flag, data = Date_base().select(sql)
        pool = {}
        proxy_max = ReadConf().proxy_pool()
        if len(data) >= proxy_max:
            Log().write_log(f"Current number of agents {proxy_max}", 'info')
            time.sleep(10)
            continue

        else:
            url = f"http://makuro.cn:22023/proxy/get_new_proxy"
            data = requests.get(url).json()
            for item in data['data']:
                IP = item['ip']
                Port = item['port']
                expire_time = item['expire_time']
                city = item['city']
                isp = item['isp']
                Log().write_log(f"GET_NEW_PROXY_IP_INFO - {IP}", 'info')


if __name__ == '__main__':
    proxy_pool()







