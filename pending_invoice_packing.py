import logging as log_
import time

import requests
from requests import request
from requests import utils
from utils.log import Log


class PendingInvoicePacking:
    def __init__(self, session_, object_ids, accident_no, cookie_packing):
        self.session_ = session_
        self.object_ids = object_ids
        self.accident_no = accident_no
        self.cookie_packing = cookie_packing

    def packing(self,):
        object_ids = ','.join(self.object_ids)

        url_ = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/packInvoiceBatch?objectIds={object_ids}&taxPayerNoInsurer=undefined'

        # 打包需要cookie
        headers_ = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Cookie': self.cookie_packing
        }

        try:
            # rep_json = request(method='POST', url=url_, headers=headers_).json()
            rep = self.session_.post(url=url_, headers=headers_)
            rep_json = rep.json()
            _, packing_id = tuple(rep_json.split('：'))  # eg：{变量‘_’：（打包成功！生成的打包号为） 变量‘packing_id’：（V66572023220100001930）}
        except Exception as e:
            print(f'事故号：{self.accident_no}打包接口异常，可能cookie错误亦或打包失败，20秒后再次打包：\n{e}')
            log_.critical(f'事故号：{self.accident_no}打包接口异常，可能cookie错误亦或打包失败，20秒后再次打包：\n{e}')
            time.sleep(20)
            return self.packing()
        else:
            if rep.status_code == 200:
                print(rep_json)
                log_.info(f'事故号：{self.accident_no}，打包反馈如下：\n{rep_json}')
                return packing_id
            else:
                print(f'事故号：{self.accident_no}打包失败，可能cookie失效！！！（状态码在400到600之间，查看是否存在客户机错误或服务器错误。状态码在200和400之间，这将返回True）')
                log_.error(f'事故号：{self.accident_no}打包失败，可能cookie失效！！！（状态码在400到600之间，查看是否存在客户机错误或服务器错误。状态码在200和400之间，这将返回True）')
                return False
        finally:
            pass






