import requests
import json
from src.module.execution_db import Date_base

url = f"http://zltiqu.pyhttp.taolop.com/getip?count=5&neek=104794&type=2&yys=0&port=1&sb=&mr=1&sep=0&ts=1"
proxy_data = requests.get(url).text
proxy_data = json.loads(proxy_data)

for item in proxy_data['data']:
    IP = item['ip']
    Port = item['port']
    expire_time = item['expire_time']
    sql = f"INSERT INTO `Paper`.`proxy_pool` (`address`, `port`, `status`, `proxy_type`, `expire_time`) VALUES ('{IP}', {Port}, '1', 'http', '{expire_time}');"
    Date_base().insert(sql)



# from flask import jsonify, request, Blueprint
# from src.log import Log
# from src.execution_db import Date_base
# import requests
# import json
#
#
# proxy_pool = Blueprint('proxy', __name__)
#
# class API:
#     @proxy_pool.route('/get_new_proxy', methods=['GET'])
#     def get_new_proxy():
#         url = f"http://zltiqu.pyhttp.taolop.com/getip?count=5&neek=104794&type=2&yys=0&port=1&sb=&mr=1&sep=0&ts=1"
#         proxy_data = requests.get(url).text
#         proxy_data = json.loads(proxy_data)
#
#         for item in proxy_data['data']:
#             IP = item['ip']
#             Port = item['port']
#             expire_time = item['expire_time']
#             sql = f"INSERT INTO `Paper`.`proxy_pool` (`address`, `port`, `status`, `proxy_type`, `count`, `expire_time`) VALUES ('{IP}', {Port}, '1', 'http', 0, '{expire_time}');"
#             Date_base().insert(sql)
#         Log().write_log(f"更新代理成功", 'I')
#         return jsonify(proxy_data), 200