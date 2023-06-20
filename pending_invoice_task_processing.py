# -*- coding: utf-8 -*-
# @Time    : 2023/4/7 11:33
# @Author  : Rik
# @Email   : 643451146@qq.com
# @File    : pending_invoice_task_processing.py

import logging as log_
import requests
from requests import request
from utils.log import Log

# objectIds 指 待打包 发票
url_ = 'http://9.0.9.11/newclaimcar/controller/claim/prpllog/prpLSwflog/findByParamInvoice?from=0&limit=10'
headers_ = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
}
# json_ = {"createEndDate":"2023-04-07T10:59:58.140+0800","createStartDate":"2023-01-07T10:59:58.140+0800","nodeType":"0,1","taskDisplayType":"0,1","businessNo":"V66572023220100001752"}
json_ = {"businessNo":"V66572023220100001774"}


Log()  # 初始化日志配置

# rep = None
try:
    # rep = request(method='POST', url=url_, headers=headers_, json=json_)
    session_ = requests.Session()
    rep = session_.post(url=url_, headers=headers_, json=json_)

except Exception as e:
    log_.critical(f'pending_invoice_task_processing程序POST接口请求出错：\n{e}')
else:
    if rep.ok:
        print(rep.json())
        log_.info(f'pending_invoice_task_processing程序POST接口请求成功')
    else:
        log_.error('响应的状态码在400到600之间，查看是否存在客户机错误或服务器错误。状态码在200和400之间，这将返回True')
finally:
    pass