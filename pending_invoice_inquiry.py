import datetime
import logging as log_
import os
import sys
import time

import requests
import schedule
from requests import request
from requests import utils

# import login

from utils.log import Log

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pending_invoice_packing import PendingInvoicePacking
from pending_invoice_verification import PendingInvoiceVerification
# from pending_invoice_image_uploading import PendingInvoiceImageUploading
from pending_invoice_image_uploading_selenium import PendingInvoiceImageUploadingSelenium


def filter_json(datasets, loss_names: list):
    print(f'查询数据量：{len(datasets)}')
    print(datasets)
    paid_amounts = []
    object_ids_ = {}
    accident_nos_ = []
    for dataset in datasets:
        loss_name = dataset.get('lossName')
        if loss_name in loss_names:
            object_id = dataset.get('objectId')  # id号
            object_ids_[str(object_id)] = loss_name

            paid_amount = dataset.get('paidAmount')  # 赔付金额
            paid_amounts.append(paid_amount)

            accident_no = dataset.get('accidentNo')  # 事故号
            accident_nos_.append(accident_no)
    print(f'损失标的：{object_ids_}')
    print(f'打包总金额：{sum(paid_amounts)}')
    print(f'事故号：{accident_nos_}')
    return object_ids_, accident_nos_


class PackInvoice:
    def __init__(self, account_name='', accident_no='', df_verification=None, df_verification2=None, loss_names=None, cookie_packing=''):
        # Log()  # 初始化日志配置
        if loss_names is None:
            loss_names = []
        self.account_name = account_name
        self.accident_no = accident_no
        self.df_verification = df_verification
        self.df_verification2 = df_verification2
        self.loss_names = loss_names
        self.cookie_packing = cookie_packing

    def start_packing(self, session_, object_ids_, invoice_fileName, invoice_path, port):
        # 打包：
        # packaging_info = PendingInvoicePacking(session_, object_ids_, self.accident_no, self.cookie_packing).packing()
        packing_id = PendingInvoicePacking(session_, object_ids_, self.accident_no, self.cookie_packing).packing()
        if packing_id:
            # _, packing_id = tuple(packaging_info.split('：'))  # eg：{变量‘_’：（打包成功！生成的打包号为） 变量‘packing_id’：（V66572023220100001930）}
            # 校验：
            # if PendingInvoiceVerification(df=self.df_verification).verify():
            if 2/1:
                # 影像上传：
                # PendingInvoiceImageUploading(packing_id).uploading_url()
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$开始影像上传$$$$$$$$$$$$$$$$$$$$$$$$$$')
                PendingInvoiceImageUploadingSelenium(packing_id, self.df_verification, self.df_verification2, self.cookie_packing, invoice_fileName, invoice_path, port=port).get_uploading_url()
                pass
            else:
                accident = self.accident_no.replace(',', '\n')
                print(f'打包号{packing_id}校验失败，请核对事故单号的发票：\n{accident}\n{"——" * 50}')
                log_.info(f'打包号{packing_id}校验失败，请核对事故单号的发票：\n{accident}\n{"——" * 50}')
        else:
            print(f'发票打包失败：{invoice_path + invoice_fileName}')
            log_.info(f'发票打包失败：{invoice_path + invoice_fileName}')
        pass


# 查询类
class QueryInvoiceReady:
    def __init__(self, accident_no, accountName):
        self.accident_no = accident_no
        self.accountName = accountName

    def query_invoice_ready(self, claimsRule=None):
        url_ = 'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/queryInvoiceReady'
        params_ = {'from': 0, 'limit': 50}
        headers_ = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        }
        json_ = {
            "batchEndTime": "",
            "batchStartTime": "",
            "state": "0",
            "certainDeptCode": "",
            "comCode": "33010000",
            "accountName": self.accountName,
            "taskFlag": "all",
            "includeDSFlag": False,
            "includeCBFlag": True,
            "tpFlag": False,
            "inLikeFlag": False,
            "accidentNoinput": self.accident_no.replace(',', '\n'),
            "accidentNo": self.accident_no
        }

        session_ = requests.Session()
        datasets = []
        try:
            rep_json = session_.post(url=url_, headers=headers_, params=params_, json=json_).json()
            entity_count = rep_json.get('entityCount$')
            if entity_count:
                for i in range(0, entity_count, 50):
                    params_inner = {'from': i, 'limit': 50}
                    rep_inner_json = session_.post(url=url_, headers=headers_, params=params_inner, json=json_).json()
                    datasets += rep_inner_json.get('data$')
            else:
                accidentNo__ = self.accident_no.replace(',', '\n')
                log_.info(f'事故号查询为空，当心已经打包过造成无法查询，请核对事故号：\n{accidentNo__}\n')

        except Exception as e:
            print(f'\n查询接口报错：\n{e}')
            log_.critical(f'查询接口报错：\n{e}')
            time.sleep(10)
            return self.query_invoice_ready()
        else:
            object_ids_ = {}
            for dataset in datasets:
                object_id = dataset.get('objectId')  # id号
                loss_name = dataset.get('lossName')  # 损失标的（即车牌号）
                object_ids_[str(object_id)] = loss_name
            return datasets, session_, object_ids_
        finally:
            pass


# # -----------------------------------------------------------------------------------------------------------
# # 初始化查询类
# obj_query = QueryInvoiceReady("80052022220000025860,80052022220000023102,80052022220000024370,80052022220000026020,80052022220000023283")
# invoice_info, session, objectID = obj_query.query_invoice_ready()
# print()
#
# # 初始化打包类
# obj_pack = PackInvoice(cookie_packing='SESSION=49c4e1c6-f2dc-481a-8133-9e2813c5b77c; _pk_ses.18.92e3=1; _pk_id.18.92e3=1bbfe1997afc172f.1680774166.; BIGipServerPool_SHDC_Portol_Auth2=814552073.22811.0000; SESSION=7a04a567-86d5-4755-a90f-f8133a99d64a; UAMSessionID=97F0BC7C4FDAF1D96C7E8E05395EA013.instance-141-48; JSESSIONID=88F992B0A9AE0B39EB265EA07002F89C.instance-164-125; BIGipServerNCS_Nginx_P80=!aaVpwe9Bs45R1IFlxDsjQ5eIaE4M2X69Z2Nz8U074LL4j4V6Pl6YdBx7Y7CzUgaV07OxqnxGAKBZLWg=; UAMAuth=89979dc5602168430160216fb03422d6; UAMauthentication=5bfc55d5-5556-499f-98df-8a4552666471; BIGipServerPool_NewClaimCounter_P7001=2562326793.22811.0000')
# obj_pack.start_packing(session, list(objectID.keys()))
# # -----------------------------------------------------------------------------------------------------------


