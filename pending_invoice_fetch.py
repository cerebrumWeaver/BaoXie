import sys
import time

import requests
import logging as log_


class PendingInvoiceFetch:
    def __init__(self):
        pass

    def fetch_invoice(self):
        # url_ = 'http://47.103.90.65:8815/api/rpa/task'
        # url_ = 'http://zphx-gpic.baoxietech.com/api/rpa/task'
        url_ = 'http://zphx-gpic-zj.baoxietech.com/api/rpa/task'
        # url_ = 'http://192.168.3.2:8815/api/rpa/task'
        headers_ = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        }
        try:
            res_json = requests.get(url_, headers=headers_).json()
            data = res_json['data']
            invoices = data['invoices']
            supplier_name = data['supplierName']
            claimNos = data['claimNos']
            claims = data['claims']
            id = data['id']
            claims_rule = []
            # 注释4个待匹配条件，后续需要取消注释
            for claim in claims:
                claim_amountPaid = claim['amountPaid']
                claim_claimNo = claim['claimNo']
                claim_paymentCaseNo = claim['paymentCaseNo']
                # claim_supplierName = claim['supplierName']
                # claims_rule.append((claim_amountPaid, claim_claimNo, claim_paymentCaseNo, claim_supplierName))
                claims_rule.append((claim_amountPaid, claim_claimNo, claim_paymentCaseNo))
            pass
        except Exception as e:
            # print(f'保携后台数据为空：休息20s。。。')
            sys.stdout.write("\033[33m")  # 设置前景色为黄色
            sys.stdout.write("保携后台数据为空：休息20s。。。\n")  # 输出文本
            log_.critical(f'保携后台数据为空：\n{e}')
            time.sleep(20)
            return self.fetch_invoice()
        else:
            # return claimNos, invoices, supplier_name
            return claimNos, invoices, supplier_name, claims_rule


# results = PendingInvoiceFetch().fetch_invoice()
# _, _, supplierName = results
# print(supplierName)
# print()


