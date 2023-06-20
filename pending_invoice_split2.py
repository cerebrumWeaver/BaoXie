import pandas as pd
import requests
import time
import logging as log_
from utils.log import Log
from invoice_data_downlaod import query_invoice_ready
from pending_invoice_inquiry import PackInvoice
from partial_deduction import PartialDeduction


class InvoicesRecords:
    def __init__(self, cookie_='', cookie_packing_=''):
        Log()  # 初始化日志配置
        # self.session = session_
        self.cookie = cookie_
        self.cookie_packing = cookie_packing_
        self.amountTotal = None  # 发票金额
        self.path = None  # 发票路径

        self.df = None
        self.invoiceNo = None  # 发票号
        self.invoiceCode = None  # 发票代码
        self.billingDate = None  # 发票日期
        self.invoiceAmount = None  # 发票金额（不含税）
        self.taxAmount = None  # 发票税额
        self.taxPayName = None  # 销方名称
        self.taxPayerNo = None  # 销方税号
        self.buyTaxPayerName = None  # 购方名称
        self.buyTaxPayerNo = None  # 购房税号
        self.invoiceRate = None  # 税率
        self.buyTaxPayerNameFace = None

        pass

    def invoices_info(self):
        datetime_ = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        datetime_ = time.strftime('%Y-%m-%d', time.strptime('2023-05-26', '%Y-%m-%d'))
        url_ = f'http://zphx-gpic-zj.baoxietech.com/invoice/datatable?draw=5&columns%5B0%5D.data=id&columns%5B0%5D.name=&columns%5B0%5D.searchable=false&columns%5B0%5D.orderable=false&columns%5B0%5D.search.value=&columns%5B0%5D.search.regex=false&columns%5B1%5D.data=id&columns%5B1%5D.name=&columns%5B1%5D.searchable=false&columns%5B1%5D.orderable=false&columns%5B1%5D.search.value=&columns%5B1%5D.search.regex=false&columns%5B2%5D.data=errorMsg&columns%5B2%5D.name=&columns%5B2%5D.searchable=true&columns%5B2%5D.orderable=true&columns%5B2%5D.search.value=&columns%5B2%5D.search.regex=false&columns%5B3%5D.data=scanDate&columns%5B3%5D.name=&columns%5B3%5D.searchable=true&columns%5B3%5D.orderable=true&columns%5B3%5D.search.value=&columns%5B3%5D.search.regex=false&columns%5B4%5D.data=batch&columns%5B4%5D.name=&columns%5B4%5D.searchable=true&columns%5B4%5D.orderable=true&columns%5B4%5D.search.value=&columns%5B4%5D.search.regex=false&columns%5B5%5D.data=sequence&columns%5B5%5D.name=&columns%5B5%5D.searchable=true&columns%5B5%5D.orderable=true&columns%5B5%5D.search.value=&columns%5B5%5D.search.regex=false&columns%5B6%5D.data=imageName&columns%5B6%5D.name=&columns%5B6%5D.searchable=true&columns%5B6%5D.orderable=true&columns%5B6%5D.search.value=&columns%5B6%5D.search.regex=false&columns%5B7%5D.data=invoicedDate&columns%5B7%5D.name=&columns%5B7%5D.searchable=true&columns%5B7%5D.orderable=true&columns%5B7%5D.search.value=&columns%5B7%5D.search.regex=false&columns%5B8%5D.data=code&columns%5B8%5D.name=&columns%5B8%5D.searchable=true&columns%5B8%5D.orderable=true&columns%5B8%5D.search.value=&columns%5B8%5D.search.regex=false&columns%5B9%5D.data=no&columns%5B9%5D.name=&columns%5B9%5D.searchable=true&columns%5B9%5D.orderable=true&columns%5B9%5D.search.value=&columns%5B9%5D.search.regex=false&columns%5B10%5D.data=branchId&columns%5B10%5D.name=&columns%5B10%5D.searchable=true&columns%5B10%5D.orderable=true&columns%5B10%5D.search.value=&columns%5B10%5D.search.regex=false&columns%5B11%5D.data=id&columns%5B11%5D.name=&columns%5B11%5D.searchable=true&columns%5B11%5D.orderable=false&columns%5B11%5D.search.value=&columns%5B11%5D.search.regex=false&columns%5B12%5D.data=supplierId&columns%5B12%5D.name=&columns%5B12%5D.searchable=true&columns%5B12%5D.orderable=false&columns%5B12%5D.search.value=&columns%5B12%5D.search.regex=false&columns%5B13%5D.data=supplierId&columns%5B13%5D.name=&columns%5B13%5D.searchable=true&columns%5B13%5D.orderable=false&columns%5B13%5D.search.value=&columns%5B13%5D.search.regex=false&columns%5B14%5D.data=amount&columns%5B14%5D.name=&columns%5B14%5D.searchable=true&columns%5B14%5D.orderable=true&columns%5B14%5D.search.value=&columns%5B14%5D.search.regex=false&columns%5B15%5D.data=amountVat&columns%5B15%5D.name=&columns%5B15%5D.searchable=true&columns%5B15%5D.orderable=true&columns%5B15%5D.search.value=&columns%5B15%5D.search.regex=false&columns%5B16%5D.data=amountTotal&columns%5B16%5D.name=&columns%5B16%5D.searchable=true&columns%5B16%5D.orderable=true&columns%5B16%5D.search.value=&columns%5B16%5D.search.regex=false&columns%5B17%5D.data=rateVat&columns%5B17%5D.name=&columns%5B17%5D.searchable=true&columns%5B17%5D.orderable=true&columns%5B17%5D.search.value=&columns%5B17%5D.search.regex=false&columns%5B18%5D.data=subject&columns%5B18%5D.name=&columns%5B18%5D.searchable=true&columns%5B18%5D.orderable=true&columns%5B18%5D.search.value=&columns%5B18%5D.search.regex=false&columns%5B19%5D.data=verificationUserId&columns%5B19%5D.name=&columns%5B19%5D.searchable=true&columns%5B19%5D.orderable=false&columns%5B19%5D.search.value=&columns%5B19%5D.search.regex=false&columns%5B20%5D.data=verificationBranchId&columns%5B20%5D.name=&columns%5B20%5D.searchable=true&columns%5B20%5D.orderable=false&columns%5B20%5D.search.value=&columns%5B20%5D.search.regex=false&order%5B0%5D.column=5&order%5B0%5D.dir=asc&start=0&length=10&search.value=&search.regex=false&batch=&imageName=&code=&no=&branchId=&supplierId=&verificationBranchId=&times={datetime_}+00%3A00+-+{datetime_}+23%3A59&status=1&valid=&enabled=&_=1686032101647'
        headers_ = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Cookie': self.cookie
        }
        recordsTotal = requests.get(url=url_, headers=headers_).json()['recordsTotal']
        if recordsTotal:
            data = []
            for i in range(0, recordsTotal, 10):
                url_ = f'http://zphx-gpic-zj.baoxietech.com/invoice/datatable?draw=5&columns%5B0%5D.data=id&columns%5B0%5D.name=&columns%5B0%5D.searchable=false&columns%5B0%5D.orderable=false&columns%5B0%5D.search.value=&columns%5B0%5D.search.regex=false&columns%5B1%5D.data=id&columns%5B1%5D.name=&columns%5B1%5D.searchable=false&columns%5B1%5D.orderable=false&columns%5B1%5D.search.value=&columns%5B1%5D.search.regex=false&columns%5B2%5D.data=errorMsg&columns%5B2%5D.name=&columns%5B2%5D.searchable=true&columns%5B2%5D.orderable=true&columns%5B2%5D.search.value=&columns%5B2%5D.search.regex=false&columns%5B3%5D.data=scanDate&columns%5B3%5D.name=&columns%5B3%5D.searchable=true&columns%5B3%5D.orderable=true&columns%5B3%5D.search.value=&columns%5B3%5D.search.regex=false&columns%5B4%5D.data=batch&columns%5B4%5D.name=&columns%5B4%5D.searchable=true&columns%5B4%5D.orderable=true&columns%5B4%5D.search.value=&columns%5B4%5D.search.regex=false&columns%5B5%5D.data=sequence&columns%5B5%5D.name=&columns%5B5%5D.searchable=true&columns%5B5%5D.orderable=true&columns%5B5%5D.search.value=&columns%5B5%5D.search.regex=false&columns%5B6%5D.data=imageName&columns%5B6%5D.name=&columns%5B6%5D.searchable=true&columns%5B6%5D.orderable=true&columns%5B6%5D.search.value=&columns%5B6%5D.search.regex=false&columns%5B7%5D.data=invoicedDate&columns%5B7%5D.name=&columns%5B7%5D.searchable=true&columns%5B7%5D.orderable=true&columns%5B7%5D.search.value=&columns%5B7%5D.search.regex=false&columns%5B8%5D.data=code&columns%5B8%5D.name=&columns%5B8%5D.searchable=true&columns%5B8%5D.orderable=true&columns%5B8%5D.search.value=&columns%5B8%5D.search.regex=false&columns%5B9%5D.data=no&columns%5B9%5D.name=&columns%5B9%5D.searchable=true&columns%5B9%5D.orderable=true&columns%5B9%5D.search.value=&columns%5B9%5D.search.regex=false&columns%5B10%5D.data=branchId&columns%5B10%5D.name=&columns%5B10%5D.searchable=true&columns%5B10%5D.orderable=true&columns%5B10%5D.search.value=&columns%5B10%5D.search.regex=false&columns%5B11%5D.data=id&columns%5B11%5D.name=&columns%5B11%5D.searchable=true&columns%5B11%5D.orderable=false&columns%5B11%5D.search.value=&columns%5B11%5D.search.regex=false&columns%5B12%5D.data=supplierId&columns%5B12%5D.name=&columns%5B12%5D.searchable=true&columns%5B12%5D.orderable=false&columns%5B12%5D.search.value=&columns%5B12%5D.search.regex=false&columns%5B13%5D.data=supplierId&columns%5B13%5D.name=&columns%5B13%5D.searchable=true&columns%5B13%5D.orderable=false&columns%5B13%5D.search.value=&columns%5B13%5D.search.regex=false&columns%5B14%5D.data=amount&columns%5B14%5D.name=&columns%5B14%5D.searchable=true&columns%5B14%5D.orderable=true&columns%5B14%5D.search.value=&columns%5B14%5D.search.regex=false&columns%5B15%5D.data=amountVat&columns%5B15%5D.name=&columns%5B15%5D.searchable=true&columns%5B15%5D.orderable=true&columns%5B15%5D.search.value=&columns%5B15%5D.search.regex=false&columns%5B16%5D.data=amountTotal&columns%5B16%5D.name=&columns%5B16%5D.searchable=true&columns%5B16%5D.orderable=true&columns%5B16%5D.search.value=&columns%5B16%5D.search.regex=false&columns%5B17%5D.data=rateVat&columns%5B17%5D.name=&columns%5B17%5D.searchable=true&columns%5B17%5D.orderable=true&columns%5B17%5D.search.value=&columns%5B17%5D.search.regex=false&columns%5B18%5D.data=subject&columns%5B18%5D.name=&columns%5B18%5D.searchable=true&columns%5B18%5D.orderable=true&columns%5B18%5D.search.value=&columns%5B18%5D.search.regex=false&columns%5B19%5D.data=verificationUserId&columns%5B19%5D.name=&columns%5B19%5D.searchable=true&columns%5B19%5D.orderable=false&columns%5B19%5D.search.value=&columns%5B19%5D.search.regex=false&columns%5B20%5D.data=verificationBranchId&columns%5B20%5D.name=&columns%5B20%5D.searchable=true&columns%5B20%5D.orderable=false&columns%5B20%5D.search.value=&columns%5B20%5D.search.regex=false&order%5B0%5D.column=5&order%5B0%5D.dir=asc&start={i}&length=10&search.value=&search.regex=false&batch=&imageName=&code=&no=&branchId=&supplierId=&verificationBranchId=&times={datetime_}+00%3A00+-+{datetime_}+23%3A59&status=1&valid=&enabled=&_=1686032101647'
                data += requests.get(url=url_, headers=headers_).json()['data']
            df = pd.json_normalize(data)
            self.df = df
            self.amountTotal = df.amountTotal  # 发票金额
            self.path = df.path   # 发票路径

            # 以下变量用于发票校验
            self.invoiceNo = df.no  # 发票号
            self.invoiceCode = df.code  # 发票代码
            self.billingDate = df.invoicedDate  # 发票日期
            self.invoiceAmount = df.amount  # # 发票金额（不含税）
            self.taxAmount = df.amountVat  # 发票税额
            self.taxPayName = df.originalSupplierName  # 销方名称
            self.taxPayerNo = df.originalSupplierTaxNo  # 销方税号
            self.buyTaxPayerName = df.branchFullName  # 购方名称
            self.buyTaxPayerNo = df.branchTaxNo  # 购房税号
            self.invoiceRate = df.rateVat  # 税率
            self.buyTaxPayerNameFace = self.buyTaxPayerName

            print(f'发票的形状{df.shape}')
        else:
            print('当日 保携后台 没有 发票图片 数据')

    def records_info(self):
        data_invoice = []
        # 根据 支付账户名称 筛选 数据
        for account_name in self.taxPayName.unique():
            if account_name:
                data_invoice += query_invoice_ready(account_name_=account_name)[0]
                pass
            pass
        if data_invoice:
            # 客户系统数据转换为表格
            df_invoice = pd.DataFrame(data_invoice)
            # 指定字段 切片
            df_fields = df_invoice[['objectId', 'accidentNo', 'accountName', 'paidAmount', 'deductibleAmount', 'payConfirmTime']]
            print(f'记录的形状{df_fields.shape}')
            # 根据时间及可拆分金额 升序排序
            df_fields = df_fields.sort_values(by=['payConfirmTime', 'deductibleAmount'])
            # 遍历每一张发票的信息
            for taxPayName, amountTotal, path in zip(self.taxPayName, self.amountTotal, self.path):
                df_fields = df_fields[(df_fields['accountName'] == taxPayName) & (df_fields['deductibleAmount'] >= amountTotal)]   # 筛选 指定销方名称（taxPayName ）
                if len(df_fields):
                    df_fields = df_fields.iloc[[0]]   # 暂先选择第一行，类型为DataFrame
                    residue_deductible_amount = df_fields.deductibleAmount.squeeze() - amountTotal
                    # 初始化查询类
                    from pending_invoice_inquiry import QueryInvoiceReady
                    obj_query = QueryInvoiceReady(accident_no=df_fields.accidentNo.squeeze(), accountName=taxPayName)
                    query_info, Session_, _ = obj_query.query_invoice_ready()
                    if residue_deductible_amount:
                        # 初始化拆分类
                        obj_deduction = PartialDeduction(invoice_info=obj_query, accident_no=df_fields.accidentNo.squeeze(), deduction_amount=df_fields.deductibleAmount.squeeze(), cookie=self.cookie_packing)
                        obj_deduction.partial_deduction(amountTotal, residue_deductible_amount)
                        # 拆分后 再查询
                        query_info, Session_, _ = obj_query.query_invoice_ready()
                        # 获取need_deduction_amount打包id
                        object_id_ = self.get_object_id(query_info, df_fields.accidentNo.squeeze(), amountTotal, df_fields)
                        print(f'object_id_值：{object_id_}')
                    else:
                        print('无需拆分')
                        object_id_ = df_fields.objectId.squeeze()
                    # 打包代码
                    # obj_pack = PackInvoice(accident_no=self.accident_no, df_verification=self.df_verification, cookie_packing=self.cookie_packing)
                    obj_pack = PackInvoice(accident_no=df_fields.accidentNo.squeeze(), df_verification2=self.df[self.df.path == path], cookie_packing=self.cookie_packing)
                    # obj_pack.start_packing(self.session, map(lambda x: str(x), object_id_list), self.invoice_fileName[index])
                    obj_pack.start_packing(Session_, [str(object_id_)], path.split('/')[-1])
                    pass
                else:
                    print(f'支付账户名称{taxPayName}对应的打包金额{amountTotal}大于{taxPayName}所有可打包金额，拆分失败！！！')
        else:
            print(f'客户系统中指定的支付账户名称查询记录为空')

    def get_object_id(self, invoice_info, accident_no, deduction_amount, fields):
        object_id_s = []
        for info in invoice_info:
            if info.get('accidentNo') == accident_no and info.get('deductibleAmount') == deduction_amount:
                object_id_s.append(info.get('objectId'))
        print(f'获取object_id_s值：{object_id_s}')
        if len(object_id_s) == 1:
            return object_id_s[0]
        else:
            for id_ in object_id_s:
                if id_ not in fields.objectId.values.tolist():
                    return id_
                pass
            return object_id_s[0]
        pass


if __name__ == '__main__':
    obj = InvoicesRecords(cookie_='ZPHX_SESSION=414350D3500482728316BB4055E2BD79', cookie_packing_='_pk_ses.18.92e3=1; BIGipServerPool_SHDC_Portol_Auth2=!tUTx/TR8zzotVsmL3UZgqG4W5Y/lOYGluw5dqbbqU55xqgXaOOfteX+6v5kUeiHt4bawAI1vMBPc/g==; UAMSessionID=367476756183440CCA66D3FDBC68F532.instance-141-49; JSESSIONID=DAA155EF3472DE8B1FDFFA7C7D3CB5FD.instance-164-127; SESSION=5c24d50a-fa62-44d0-a042-dfaa72787c8b; BIGipServerNCS_Nginx_P80=!Rig7q+v3RpfZYwZlxDsjQ5eIaE4M2SZ4gbBAvAzmmTaqeQX6BjOSK2in0I2vM38o2TomrvmRvDtPtZs=; BIGipServerPool_Matomo_T033_P8000=!qd9I9c9SBwlnX65lxDsjQ5eIaE4M2coMsCrsy/bUAZo+AAcFbH8QrWyGp7t6uHtx5X4qhyH3/ime7Es=; SESSION=53e7c006-0037-4794-9173-2078e0770d22; BIGipServerPool_NewClaimCounter_P7001=1991508233.22811.0000; UAMAuth=89979dc67155bfc901719aa0f11d1740; _pk_id.18.92e3=12539645dd172b44.1686981219.; UAMauthentication=e11927c1-6b29-4afc-8572-ee562b504352')
    obj.invoices_info()  # 发票信息 提取
    obj.records_info()
