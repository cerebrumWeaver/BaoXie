import pandas as pd
import numpy as np
import os
import requests
import time
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp


# 从客户系统爬数据
def query_invoice_ready(account_name_=''):
    url_ = 'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/queryInvoiceReady'
    params_ = {'from': 0, 'limit': 50}
    headers_ = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    }
    json_ = {
        "payConfirmEndTime": f"{pd.Timestamp(datetime.now()).strftime('%Y-%m-%d')}T23:59:59.000+0800",
        "payConfirmStartTime": f"{pd.Timestamp(year=datetime.now().year - 3, month=datetime.now().month, day=datetime.now().day).strftime('%Y-%m-%d')}T00:00:00.000+0800",
        "batchEndTime": "",
        "batchStartTime": "",
        "state": "0",
        "certainDeptCode": "",
        "comCode": "33010000",
        "accountName": account_name_,
        "taskFlag": "all",
        "includeDSFlag": False,
        "includeCBFlag": True,
        "tpFlag": False,
        "inLikeFlag": False
    }

    session_ = requests.Session()
    datasets = []
    try:
        rep_json = session_.post(url=url_, headers=headers_, params=params_, json=json_).json()
        entity_count = rep_json.get('entityCount$')
        if entity_count:
            for i in range(0, entity_count, 500):
                params_inner = {'from': i, 'limit': 500}
                rep_inner_json = session_.post(url=url_, headers=headers_, params=params_inner, json=json_).json()
                datasets += rep_inner_json.get('data$')
    #         else:
    #             accidentNo__ = self.accident_no.replace(',', '\n')

    except Exception as e:
        print(f'\n休眠2s钟后重新查询支付账户名称：{account_name_}，因为客户系统查询接口报错：\n{e}')
        time.sleep(2)
        return query_invoice_ready(account_name_=account_name_)
    else:
        object_ids_ = {}
        for dataset in datasets:
            object_id = dataset.get('objectId')  # id号
            loss_name = dataset.get('lossName')  # 损失标的（即车牌号）
            object_ids_[str(object_id)] = loss_name
        return datasets, session_, object_ids_
    finally:
        pass


async def query_invoice_ready_timedelta(session, url, headers, params, json):
    async with session.post(url=url, headers=headers, params=params, json=json) as rep:
        await rep.json()
    pass


def get_timedelta():
    current_date = datetime.now()
    json_list = []
    for _ in range(5):
        end_time = pd.Timestamp(current_date).strftime('%Y-%m-%d')
        start_time = pd.Timestamp(datetime.strptime(end_time, '%Y-%m-%d') - timedelta(days=180)).strftime('%Y-%m-%d')
        current_date = start_time
        json_ = {
            "payConfirmEndTime": f"{end_time}T23:59:59.000+0800",
            "payConfirmStartTime": f"{start_time}T23:59:59.000+0800",
            "batchEndTime": "",
            "batchStartTime": "",
            "state": "0",
            "certainDeptCode": "",
            "comCode": "33010000",
            "accountName": '',
            "taskFlag": "all",
            "includeDSFlag": False,
            "includeCBFlag": True,
            "tpFlag": False,
            "inLikeFlag": False
        }
        json_list.append(json_)
    return json_list


if __name__ == '__main__':
    datetime_ = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # datetime_ = time.strftime('%Y-%m-%d', time.strptime('2023-05-26', '%Y-%m-%d'))
    url_ = f'http://zphx-gpic-zj.baoxietech.com/invoice/datatable?draw=5&columns%5B0%5D.data=id&columns%5B0%5D.name=&columns%5B0%5D.searchable=false&columns%5B0%5D.orderable=false&columns%5B0%5D.search.value=&columns%5B0%5D.search.regex=false&columns%5B1%5D.data=id&columns%5B1%5D.name=&columns%5B1%5D.searchable=false&columns%5B1%5D.orderable=false&columns%5B1%5D.search.value=&columns%5B1%5D.search.regex=false&columns%5B2%5D.data=errorMsg&columns%5B2%5D.name=&columns%5B2%5D.searchable=true&columns%5B2%5D.orderable=true&columns%5B2%5D.search.value=&columns%5B2%5D.search.regex=false&columns%5B3%5D.data=scanDate&columns%5B3%5D.name=&columns%5B3%5D.searchable=true&columns%5B3%5D.orderable=true&columns%5B3%5D.search.value=&columns%5B3%5D.search.regex=false&columns%5B4%5D.data=batch&columns%5B4%5D.name=&columns%5B4%5D.searchable=true&columns%5B4%5D.orderable=true&columns%5B4%5D.search.value=&columns%5B4%5D.search.regex=false&columns%5B5%5D.data=sequence&columns%5B5%5D.name=&columns%5B5%5D.searchable=true&columns%5B5%5D.orderable=true&columns%5B5%5D.search.value=&columns%5B5%5D.search.regex=false&columns%5B6%5D.data=imageName&columns%5B6%5D.name=&columns%5B6%5D.searchable=true&columns%5B6%5D.orderable=true&columns%5B6%5D.search.value=&columns%5B6%5D.search.regex=false&columns%5B7%5D.data=invoicedDate&columns%5B7%5D.name=&columns%5B7%5D.searchable=true&columns%5B7%5D.orderable=true&columns%5B7%5D.search.value=&columns%5B7%5D.search.regex=false&columns%5B8%5D.data=code&columns%5B8%5D.name=&columns%5B8%5D.searchable=true&columns%5B8%5D.orderable=true&columns%5B8%5D.search.value=&columns%5B8%5D.search.regex=false&columns%5B9%5D.data=no&columns%5B9%5D.name=&columns%5B9%5D.searchable=true&columns%5B9%5D.orderable=true&columns%5B9%5D.search.value=&columns%5B9%5D.search.regex=false&columns%5B10%5D.data=branchId&columns%5B10%5D.name=&columns%5B10%5D.searchable=true&columns%5B10%5D.orderable=true&columns%5B10%5D.search.value=&columns%5B10%5D.search.regex=false&columns%5B11%5D.data=id&columns%5B11%5D.name=&columns%5B11%5D.searchable=true&columns%5B11%5D.orderable=false&columns%5B11%5D.search.value=&columns%5B11%5D.search.regex=false&columns%5B12%5D.data=supplierId&columns%5B12%5D.name=&columns%5B12%5D.searchable=true&columns%5B12%5D.orderable=false&columns%5B12%5D.search.value=&columns%5B12%5D.search.regex=false&columns%5B13%5D.data=supplierId&columns%5B13%5D.name=&columns%5B13%5D.searchable=true&columns%5B13%5D.orderable=false&columns%5B13%5D.search.value=&columns%5B13%5D.search.regex=false&columns%5B14%5D.data=amount&columns%5B14%5D.name=&columns%5B14%5D.searchable=true&columns%5B14%5D.orderable=true&columns%5B14%5D.search.value=&columns%5B14%5D.search.regex=false&columns%5B15%5D.data=amountVat&columns%5B15%5D.name=&columns%5B15%5D.searchable=true&columns%5B15%5D.orderable=true&columns%5B15%5D.search.value=&columns%5B15%5D.search.regex=false&columns%5B16%5D.data=amountTotal&columns%5B16%5D.name=&columns%5B16%5D.searchable=true&columns%5B16%5D.orderable=true&columns%5B16%5D.search.value=&columns%5B16%5D.search.regex=false&columns%5B17%5D.data=rateVat&columns%5B17%5D.name=&columns%5B17%5D.searchable=true&columns%5B17%5D.orderable=true&columns%5B17%5D.search.value=&columns%5B17%5D.search.regex=false&columns%5B18%5D.data=subject&columns%5B18%5D.name=&columns%5B18%5D.searchable=true&columns%5B18%5D.orderable=true&columns%5B18%5D.search.value=&columns%5B18%5D.search.regex=false&columns%5B19%5D.data=verificationUserId&columns%5B19%5D.name=&columns%5B19%5D.searchable=true&columns%5B19%5D.orderable=false&columns%5B19%5D.search.value=&columns%5B19%5D.search.regex=false&columns%5B20%5D.data=verificationBranchId&columns%5B20%5D.name=&columns%5B20%5D.searchable=true&columns%5B20%5D.orderable=false&columns%5B20%5D.search.value=&columns%5B20%5D.search.regex=false&order%5B0%5D.column=4&order%5B0%5D.dir=desc&order%5B1%5D.column=5&order%5B1%5D.dir=asc&start=0&length=10&search.value=&search.regex=false&batch=+&imageName=+&code=+&no=+&branchId=&supplierId=&verificationBranchId=&times=+&status=1&valid=&enabled=&_=1687146661355'
    # url_ = f'http://zphx-gpic-zj.baoxietech.com/invoice/datatable?draw=5&columns%5B0%5D.data=id&columns%5B0%5D.name=&columns%5B0%5D.searchable=false&columns%5B0%5D.orderable=false&columns%5B0%5D.search.value=&columns%5B0%5D.search.regex=false&columns%5B1%5D.data=id&columns%5B1%5D.name=&columns%5B1%5D.searchable=false&columns%5B1%5D.orderable=false&columns%5B1%5D.search.value=&columns%5B1%5D.search.regex=false&columns%5B2%5D.data=errorMsg&columns%5B2%5D.name=&columns%5B2%5D.searchable=true&columns%5B2%5D.orderable=true&columns%5B2%5D.search.value=&columns%5B2%5D.search.regex=false&columns%5B3%5D.data=scanDate&columns%5B3%5D.name=&columns%5B3%5D.searchable=true&columns%5B3%5D.orderable=true&columns%5B3%5D.search.value=&columns%5B3%5D.search.regex=false&columns%5B4%5D.data=batch&columns%5B4%5D.name=&columns%5B4%5D.searchable=true&columns%5B4%5D.orderable=true&columns%5B4%5D.search.value=&columns%5B4%5D.search.regex=false&columns%5B5%5D.data=sequence&columns%5B5%5D.name=&columns%5B5%5D.searchable=true&columns%5B5%5D.orderable=true&columns%5B5%5D.search.value=&columns%5B5%5D.search.regex=false&columns%5B6%5D.data=imageName&columns%5B6%5D.name=&columns%5B6%5D.searchable=true&columns%5B6%5D.orderable=true&columns%5B6%5D.search.value=&columns%5B6%5D.search.regex=false&columns%5B7%5D.data=invoicedDate&columns%5B7%5D.name=&columns%5B7%5D.searchable=true&columns%5B7%5D.orderable=true&columns%5B7%5D.search.value=&columns%5B7%5D.search.regex=false&columns%5B8%5D.data=code&columns%5B8%5D.name=&columns%5B8%5D.searchable=true&columns%5B8%5D.orderable=true&columns%5B8%5D.search.value=&columns%5B8%5D.search.regex=false&columns%5B9%5D.data=no&columns%5B9%5D.name=&columns%5B9%5D.searchable=true&columns%5B9%5D.orderable=true&columns%5B9%5D.search.value=&columns%5B9%5D.search.regex=false&columns%5B10%5D.data=branchId&columns%5B10%5D.name=&columns%5B10%5D.searchable=true&columns%5B10%5D.orderable=true&columns%5B10%5D.search.value=&columns%5B10%5D.search.regex=false&columns%5B11%5D.data=id&columns%5B11%5D.name=&columns%5B11%5D.searchable=true&columns%5B11%5D.orderable=false&columns%5B11%5D.search.value=&columns%5B11%5D.search.regex=false&columns%5B12%5D.data=supplierId&columns%5B12%5D.name=&columns%5B12%5D.searchable=true&columns%5B12%5D.orderable=false&columns%5B12%5D.search.value=&columns%5B12%5D.search.regex=false&columns%5B13%5D.data=supplierId&columns%5B13%5D.name=&columns%5B13%5D.searchable=true&columns%5B13%5D.orderable=false&columns%5B13%5D.search.value=&columns%5B13%5D.search.regex=false&columns%5B14%5D.data=amount&columns%5B14%5D.name=&columns%5B14%5D.searchable=true&columns%5B14%5D.orderable=true&columns%5B14%5D.search.value=&columns%5B14%5D.search.regex=false&columns%5B15%5D.data=amountVat&columns%5B15%5D.name=&columns%5B15%5D.searchable=true&columns%5B15%5D.orderable=true&columns%5B15%5D.search.value=&columns%5B15%5D.search.regex=false&columns%5B16%5D.data=amountTotal&columns%5B16%5D.name=&columns%5B16%5D.searchable=true&columns%5B16%5D.orderable=true&columns%5B16%5D.search.value=&columns%5B16%5D.search.regex=false&columns%5B17%5D.data=rateVat&columns%5B17%5D.name=&columns%5B17%5D.searchable=true&columns%5B17%5D.orderable=true&columns%5B17%5D.search.value=&columns%5B17%5D.search.regex=false&columns%5B18%5D.data=subject&columns%5B18%5D.name=&columns%5B18%5D.searchable=true&columns%5B18%5D.orderable=true&columns%5B18%5D.search.value=&columns%5B18%5D.search.regex=false&columns%5B19%5D.data=verificationUserId&columns%5B19%5D.name=&columns%5B19%5D.searchable=true&columns%5B19%5D.orderable=false&columns%5B19%5D.search.value=&columns%5B19%5D.search.regex=false&columns%5B20%5D.data=verificationBranchId&columns%5B20%5D.name=&columns%5B20%5D.searchable=true&columns%5B20%5D.orderable=false&columns%5B20%5D.search.value=&columns%5B20%5D.search.regex=false&order%5B0%5D.column=5&order%5B0%5D.dir=asc&start=0&length=10&search.value=&search.regex=false&batch=&imageName=&code=&no=&branchId=&supplierId=&verificationBranchId=&times={datetime_}+00%3A00+-+{datetime_}+23%3A59&status=1&valid=&enabled=&_=1686032101647'
    headers_ = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Cookie': 'ZPHX_SESSION=414350D3500482728316BB4055E2BD79'
    }
    recordsTotal = requests.get(url=url_, headers=headers_).json()['recordsTotal']
    if recordsTotal:
        data = []
        for i in range(0, recordsTotal, 10):
            print(i)
            url_ = f'http://zphx-gpic-zj.baoxietech.com/invoice/datatable?draw=5&columns%5B0%5D.data=id&columns%5B0%5D.name=&columns%5B0%5D.searchable=false&columns%5B0%5D.orderable=false&columns%5B0%5D.search.value=&columns%5B0%5D.search.regex=false&columns%5B1%5D.data=id&columns%5B1%5D.name=&columns%5B1%5D.searchable=false&columns%5B1%5D.orderable=false&columns%5B1%5D.search.value=&columns%5B1%5D.search.regex=false&columns%5B2%5D.data=errorMsg&columns%5B2%5D.name=&columns%5B2%5D.searchable=true&columns%5B2%5D.orderable=true&columns%5B2%5D.search.value=&columns%5B2%5D.search.regex=false&columns%5B3%5D.data=scanDate&columns%5B3%5D.name=&columns%5B3%5D.searchable=true&columns%5B3%5D.orderable=true&columns%5B3%5D.search.value=&columns%5B3%5D.search.regex=false&columns%5B4%5D.data=batch&columns%5B4%5D.name=&columns%5B4%5D.searchable=true&columns%5B4%5D.orderable=true&columns%5B4%5D.search.value=&columns%5B4%5D.search.regex=false&columns%5B5%5D.data=sequence&columns%5B5%5D.name=&columns%5B5%5D.searchable=true&columns%5B5%5D.orderable=true&columns%5B5%5D.search.value=&columns%5B5%5D.search.regex=false&columns%5B6%5D.data=imageName&columns%5B6%5D.name=&columns%5B6%5D.searchable=true&columns%5B6%5D.orderable=true&columns%5B6%5D.search.value=&columns%5B6%5D.search.regex=false&columns%5B7%5D.data=invoicedDate&columns%5B7%5D.name=&columns%5B7%5D.searchable=true&columns%5B7%5D.orderable=true&columns%5B7%5D.search.value=&columns%5B7%5D.search.regex=false&columns%5B8%5D.data=code&columns%5B8%5D.name=&columns%5B8%5D.searchable=true&columns%5B8%5D.orderable=true&columns%5B8%5D.search.value=&columns%5B8%5D.search.regex=false&columns%5B9%5D.data=no&columns%5B9%5D.name=&columns%5B9%5D.searchable=true&columns%5B9%5D.orderable=true&columns%5B9%5D.search.value=&columns%5B9%5D.search.regex=false&columns%5B10%5D.data=branchId&columns%5B10%5D.name=&columns%5B10%5D.searchable=true&columns%5B10%5D.orderable=true&columns%5B10%5D.search.value=&columns%5B10%5D.search.regex=false&columns%5B11%5D.data=id&columns%5B11%5D.name=&columns%5B11%5D.searchable=true&columns%5B11%5D.orderable=false&columns%5B11%5D.search.value=&columns%5B11%5D.search.regex=false&columns%5B12%5D.data=supplierId&columns%5B12%5D.name=&columns%5B12%5D.searchable=true&columns%5B12%5D.orderable=false&columns%5B12%5D.search.value=&columns%5B12%5D.search.regex=false&columns%5B13%5D.data=supplierId&columns%5B13%5D.name=&columns%5B13%5D.searchable=true&columns%5B13%5D.orderable=false&columns%5B13%5D.search.value=&columns%5B13%5D.search.regex=false&columns%5B14%5D.data=amount&columns%5B14%5D.name=&columns%5B14%5D.searchable=true&columns%5B14%5D.orderable=true&columns%5B14%5D.search.value=&columns%5B14%5D.search.regex=false&columns%5B15%5D.data=amountVat&columns%5B15%5D.name=&columns%5B15%5D.searchable=true&columns%5B15%5D.orderable=true&columns%5B15%5D.search.value=&columns%5B15%5D.search.regex=false&columns%5B16%5D.data=amountTotal&columns%5B16%5D.name=&columns%5B16%5D.searchable=true&columns%5B16%5D.orderable=true&columns%5B16%5D.search.value=&columns%5B16%5D.search.regex=false&columns%5B17%5D.data=rateVat&columns%5B17%5D.name=&columns%5B17%5D.searchable=true&columns%5B17%5D.orderable=true&columns%5B17%5D.search.value=&columns%5B17%5D.search.regex=false&columns%5B18%5D.data=subject&columns%5B18%5D.name=&columns%5B18%5D.searchable=true&columns%5B18%5D.orderable=true&columns%5B18%5D.search.value=&columns%5B18%5D.search.regex=false&columns%5B19%5D.data=verificationUserId&columns%5B19%5D.name=&columns%5B19%5D.searchable=true&columns%5B19%5D.orderable=false&columns%5B19%5D.search.value=&columns%5B19%5D.search.regex=false&columns%5B20%5D.data=verificationBranchId&columns%5B20%5D.name=&columns%5B20%5D.searchable=true&columns%5B20%5D.orderable=false&columns%5B20%5D.search.value=&columns%5B20%5D.search.regex=false&order%5B0%5D.column=4&order%5B0%5D.dir=desc&order%5B1%5D.column=5&order%5B1%5D.dir=asc&start={i}&length=10&search.value=&search.regex=false&batch=+&imageName=+&code=+&no=+&branchId=&supplierId=&verificationBranchId=&times=+&status=1&valid=&enabled=&_=1687146661355'
            # url_ = f'http://zphx-gpic-zj.baoxietech.com/invoice/datatable?draw=5&columns%5B0%5D.data=id&columns%5B0%5D.name=&columns%5B0%5D.searchable=false&columns%5B0%5D.orderable=false&columns%5B0%5D.search.value=&columns%5B0%5D.search.regex=false&columns%5B1%5D.data=id&columns%5B1%5D.name=&columns%5B1%5D.searchable=false&columns%5B1%5D.orderable=false&columns%5B1%5D.search.value=&columns%5B1%5D.search.regex=false&columns%5B2%5D.data=errorMsg&columns%5B2%5D.name=&columns%5B2%5D.searchable=true&columns%5B2%5D.orderable=true&columns%5B2%5D.search.value=&columns%5B2%5D.search.regex=false&columns%5B3%5D.data=scanDate&columns%5B3%5D.name=&columns%5B3%5D.searchable=true&columns%5B3%5D.orderable=true&columns%5B3%5D.search.value=&columns%5B3%5D.search.regex=false&columns%5B4%5D.data=batch&columns%5B4%5D.name=&columns%5B4%5D.searchable=true&columns%5B4%5D.orderable=true&columns%5B4%5D.search.value=&columns%5B4%5D.search.regex=false&columns%5B5%5D.data=sequence&columns%5B5%5D.name=&columns%5B5%5D.searchable=true&columns%5B5%5D.orderable=true&columns%5B5%5D.search.value=&columns%5B5%5D.search.regex=false&columns%5B6%5D.data=imageName&columns%5B6%5D.name=&columns%5B6%5D.searchable=true&columns%5B6%5D.orderable=true&columns%5B6%5D.search.value=&columns%5B6%5D.search.regex=false&columns%5B7%5D.data=invoicedDate&columns%5B7%5D.name=&columns%5B7%5D.searchable=true&columns%5B7%5D.orderable=true&columns%5B7%5D.search.value=&columns%5B7%5D.search.regex=false&columns%5B8%5D.data=code&columns%5B8%5D.name=&columns%5B8%5D.searchable=true&columns%5B8%5D.orderable=true&columns%5B8%5D.search.value=&columns%5B8%5D.search.regex=false&columns%5B9%5D.data=no&columns%5B9%5D.name=&columns%5B9%5D.searchable=true&columns%5B9%5D.orderable=true&columns%5B9%5D.search.value=&columns%5B9%5D.search.regex=false&columns%5B10%5D.data=branchId&columns%5B10%5D.name=&columns%5B10%5D.searchable=true&columns%5B10%5D.orderable=true&columns%5B10%5D.search.value=&columns%5B10%5D.search.regex=false&columns%5B11%5D.data=id&columns%5B11%5D.name=&columns%5B11%5D.searchable=true&columns%5B11%5D.orderable=false&columns%5B11%5D.search.value=&columns%5B11%5D.search.regex=false&columns%5B12%5D.data=supplierId&columns%5B12%5D.name=&columns%5B12%5D.searchable=true&columns%5B12%5D.orderable=false&columns%5B12%5D.search.value=&columns%5B12%5D.search.regex=false&columns%5B13%5D.data=supplierId&columns%5B13%5D.name=&columns%5B13%5D.searchable=true&columns%5B13%5D.orderable=false&columns%5B13%5D.search.value=&columns%5B13%5D.search.regex=false&columns%5B14%5D.data=amount&columns%5B14%5D.name=&columns%5B14%5D.searchable=true&columns%5B14%5D.orderable=true&columns%5B14%5D.search.value=&columns%5B14%5D.search.regex=false&columns%5B15%5D.data=amountVat&columns%5B15%5D.name=&columns%5B15%5D.searchable=true&columns%5B15%5D.orderable=true&columns%5B15%5D.search.value=&columns%5B15%5D.search.regex=false&columns%5B16%5D.data=amountTotal&columns%5B16%5D.name=&columns%5B16%5D.searchable=true&columns%5B16%5D.orderable=true&columns%5B16%5D.search.value=&columns%5B16%5D.search.regex=false&columns%5B17%5D.data=rateVat&columns%5B17%5D.name=&columns%5B17%5D.searchable=true&columns%5B17%5D.orderable=true&columns%5B17%5D.search.value=&columns%5B17%5D.search.regex=false&columns%5B18%5D.data=subject&columns%5B18%5D.name=&columns%5B18%5D.searchable=true&columns%5B18%5D.orderable=true&columns%5B18%5D.search.value=&columns%5B18%5D.search.regex=false&columns%5B19%5D.data=verificationUserId&columns%5B19%5D.name=&columns%5B19%5D.searchable=true&columns%5B19%5D.orderable=false&columns%5B19%5D.search.value=&columns%5B19%5D.search.regex=false&columns%5B20%5D.data=verificationBranchId&columns%5B20%5D.name=&columns%5B20%5D.searchable=true&columns%5B20%5D.orderable=false&columns%5B20%5D.search.value=&columns%5B20%5D.search.regex=false&order%5B0%5D.column=5&order%5B0%5D.dir=asc&start={i}&length=10&search.value=&search.regex=false&batch=&imageName=&code=&no=&branchId=&supplierId=&verificationBranchId=&times={datetime_}+00%3A00+-+{datetime_}+23%3A59&status=1&valid=&enabled=&_=1686032101647'
            data += requests.get(url=url_, headers=headers_).json()['data']
        df = pd.json_normalize(data)
        print(f'发票未匹配的形状{df.shape}，支付账户名称有：{df.originalSupplierName.unique()}')
        data2 = []
        for account_name in df.originalSupplierName.unique():
            if account_name:
                data2 += query_invoice_ready(account_name_=account_name)[0]
                pass
            pass
        df_download = pd.DataFrame(data2)
        print(df_download.shape)
        certain_code_name = df_download.certainCode + '-' + df_download.certainName

        df_import = df_download[['accidentNo', 'certiNo', 'deductibleAmount', 'accountName', 'payConfirmTime', 'compensateRemark']].rename(
            columns={'accidentNo': '报案号', 'certiNo': '赔案号', 'deductibleAmount': '金额', 'accountName': '收款人', 'payConfirmTime': '核赔通过时间', 'compensateRemark': '理算书备注信息'})
        df_import.insert(loc=0, column='承保分公司', value='国寿浙江')
        df_import.insert(loc=1, column='承保中支公司', value='国寿杭州')
        df_import.insert(loc=4, column='赔款或费用类型', value='赔款收据')
        df_import.insert(loc=5, column='发票类型', value='待补票')
        df_import.insert(loc=8, column='理算人姓名+UM工号', value=certain_code_name)
        df_import['理算人姓名+UM工号'].fillna('-', inplace=True)
        print('下载结束')
        save_file_path = r"C:\Users\baoxie111\Desktop\hz_file"
        file_name = f'{datetime_}merge'
        df_import.to_excel(f'{os.path.join(save_file_path, file_name)}_account.xlsx', index=False)
        print('保存结束')
    else:
        print('保携后台系统没有当天上传发票信息')
