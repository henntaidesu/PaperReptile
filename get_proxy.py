from src.module.execution_db import DB
from src.module.now_time import proxy_time
from src.module.log import Log, err2
from src.module.read_conf import ReadConf
import requests
import time
import json


def proxy_pool():
    while True:
        sql = f"SELECT * FROM `proxy_pool` where `status` = '1' and expire_time > '{proxy_time()}'"
        proxy_max, url = ReadConf().proxy_pool()
        flag, data = DB().select(sql)
        if len(data) >= proxy_max:
            Log().write_log(f"Current number of agents {proxy_max}", 'info')
            time.sleep(30)
            continue

        else:
            try:
                proxy_data = requests.get(url).text
                proxy_data = json.loads(proxy_data)
                if proxy_data['success'] is False:
                    if proxy_data['msg'] == '今日套餐已用完':
                        Log().write_log(f"今日套餐已用完", 'warning')
                        time.sleep(600)
                    else:
                        Log().write_log(f"{proxy_data['msg']}", 'error')
                else:
                    for item in proxy_data['data']:
                        IP = item['ip']
                        Port = item['port']
                        expire_time = item['expire_time']
                        city = item['city']
                        isp = item['isp']
                        sql = f"INSERT INTO `Paper`.`proxy_pool` (`address`, `port`, `status`, `proxy_type`, `expire_time`, `city`, `isp`) VALUES ('{IP}', {Port}, '1', 'http', '{expire_time}', '{city}', '{isp}');"
                        DB().insert(sql)
                        Log().write_log(f"GET_NEW_PROXY_IP_INFO - {IP} - {city}", 'info')
                    time.sleep(60)
            except Exception as e:
                err2(e)


if __name__ == '__main__':
    proxy_pool()







