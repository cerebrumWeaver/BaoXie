import logging as log_
import time
import pandas as pd

from requests import request

from pending_invoice_fetch import PendingInvoiceFetch
from utils.log import Log


class PendingInvoiceVerification:
    def __init__(self, df):
        self.invoiceNo = df.no.squeeze()
        self.invoiceCode = df.code.squeeze()
        self.billingDate = df.invoicedDate.squeeze()
        self.invoiceAmount = df.amount.squeeze()
        self.taxAmount = df.amountVat.squeeze()
        self.taxPayName = df['supplier.fullname'].squeeze()
        self.taxPayerNo = df['supplier.taxNo'].squeeze()
        self.buyTaxPayerName = df['branch.fullname'].squeeze()
        self.buyTaxPayerNo = df['branch.taxNo'].squeeze()
        self.invoiceRate = df.rateVat.squeeze()
        self.buyTaxPayerNameFace = self.buyTaxPayerName

    def verify(self):
        headers_ = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Cookie': 'SESSION=3abcfa7f-ed70-4d56-9715-ece5c39b97e8; _pk_id.18.92e3=1d96324aa15db994.1684389912.; _pk_ses.18.92e3=1; BIGipServerNCS_Nginx_P80=!7vDNgVAyS44aE3xlxDsjQ5eIaE4M2U3+cTsSHBzStXAy8qxzdL8VHb9YyaKSzxjzzHmb0MP17Skyqgw=; SESSION=4714eb35-dd63-4cfd-901f-d235d1942d1c; UAMSessionID=B4358A839F7D4C980A6366E93034F4B3.instance-159-97; UAMAuth=89979dc67155bfc901719aa0f11d1740; UAMauthentication=6dfc6110-910c-4139-b13e-957886e3788c; BIGipServerPool_SHDC_Portol_Auth2=!Jlnzg7VvosRfBpCL3UZgqG4W5Y/lOWqMJK4nBRLs3DgTGqz0pnpc3V/+qIIvh0lKuiwC3yCixkZ2rKc=; BIGipServerPool_NewClaimCounter_P7001=1941176585.22811.0000; BIGipServerPool_Matomo_T033_P8000=!JsBscXsub3pyrHxlxDsjQ5eIaE4M2UyJY01picftf8/kaoF9B1NFdlWHwnYtRScmNCfLLplULn+9UF0=',

        }
        json_ = {
            "invoiceType": "1",
            "deductionItem": "1",
            "invoiceNo": "03641706",
            "invoiceCode": "3300231130",
            "billingDate": "2023-04-26",
            "invoiceAmount": 2212.39,
            "taxAmount": 287.61,
            "taxPayName": "浙江元通之星汽车有限公司",
            "taxPayerNo": "91330103MA2KJB6J67",
            "buyTaxPayerName": "中国人寿财产保险股份有限公司杭州市中心支公司",
            "buyTaxPayerNo": "913300006912899498",
            "inStatusCode": "01",
            "invoiceRate": "13.00",
            "validateSignFlag": "",
            "buyTaxPayerNameFace": "中国人寿财产保险股份有限公司杭州市中心支公司"
        }

        json_ = {
            "invoiceType": "1",  # 发票类型
            "invoiceNo": self.invoiceNo,  # 发票号码
            "invoiceCode": self.invoiceCode,  # 发票代码
            "billingDate": f"{self.billingDate}T00:00:00.000+0800",  # 开票日期
            "invoiceAmount": self.invoiceAmount,  # 发票金额（不含税）
            "taxAmount": self.taxAmount,  # 税额
            "taxPayName": self.taxPayName,  # 销方
            "taxPayerNo": self.taxPayerNo,
            "buyTaxPayerName": self.buyTaxPayerName,
            "buyTaxPayerNo": self.buyTaxPayerNo,
            "inStatusCode": "",  # 发票状态
            "invoiceRate": self.invoiceRate,  # 税率
            "deductionItem": "1",  # 抵扣项目
            "validateSignFlag": "",
            "buyTaxPayerNameFace": self.buyTaxPayerNameFace  # 购方
        }

        url_ = 'http://9.0.9.11/newclaimcar/controller/claim/prplinvoicepre/prpLInvoicePre/invoiceDealCheck'
        # Log()  # 初始化日志配置

        try:
            rep_json = request(method='POST', url=url_, headers=headers_, json=json_).json()
        except Exception as e:
            print(f'校验接口报错：\n{e}')
            log_.critical(f'校验接口报错：\n{e}')
            time.sleep(10)
            return self.verify()
        else:
            if rep_json['inStatusCode'] == '01':
                print(rep_json)  # 通过校验
                log_.info(rep_json)
                return True
            else:
                return False
        finally:
            pass


if __name__ == '__main__':
    PendingInvoiceVerification(pd.json_normalize(PendingInvoiceFetch().fetch_invoice()[1])).verify()




