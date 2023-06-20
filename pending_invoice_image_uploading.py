# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 16:06
# @Author  : Rik
# @Email   : 643451146@qq.com
# @File    : pending_invoice_image_uploading.py

import logging as log_
import requests
from requests import request
from utils.log import Log


class PendingInvoiceImageUploading:
    def __init__(self, packing_id):
        self.packing_id = packing_id
        pass

    def uploading_url(self):
        image_uploading_urls = []
        # register_no = '8605212022220000021719'  # 报案号
        headers_ = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        }

        Log()  # 初始化日志配置

        try:
            # rep = request(method='POST', url=url_, headers=headers_)
            session_ = requests.Session()
            url_packing_info = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/queryPrpLInvoiceReadyList?batchNo={self.packing_id}'
            packing_info = session_.post(url=url_packing_info, headers=headers_).json()
            register_no_s = []
            # 合并以下两个for循环
            for info in packing_info['prplInvoiceReadyEOList']:
                register_no = info['registNo']
                register_no_s.append(register_no)
                url_ = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoicedetailmain/prplInvoiceDetailMain/openImageByUrl?registNo={register_no}'
                rep = session_.post(url=url_, headers=headers_)
                if rep.ok:
                    image_uploading_urls.append(rep.json())
                    
                else:
                    log_.error('pending_invoice_packing程序响应的状态码在400到600之间，查看是否存在客户机错误或服务器错误。状态码在200和400之间，这将返回True')

            # for register_no in register_no_s:
            #     url_ = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoicedetailmain/prplInvoiceDetailMain/openImageByUrl?registNo={register_no}'
            #     rep = session_.post(url=url_, headers=headers_)
            #     if rep.ok:
            #         image_uploading_urls.append(rep.text)
            #     else:
            #         log_.error(
            #             'pending_invoice_packing程序响应的状态码在400到600之间，查看是否存在客户机错误或服务器错误。状态码在200和400之间，这将返回True')
        except Exception as e:
            log_.critical(f'pending_invoice_packing程序POST接口请求出错：\n{e}')
        else:
            log_.info(f'pending_invoice_packing程序POST接口所有影像上传成功')
            log_.info(f'pending_invoice_packing程序影像上传链接有：{image_uploading_urls}')
            print(image_uploading_urls)
        finally:
            pass

    def uploading_image(self, urls=[]):

        pass
