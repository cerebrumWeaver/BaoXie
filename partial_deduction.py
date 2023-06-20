import requests
import copy
import pandas as pd
from pending_invoice_inquiry import QueryInvoiceReady


class PartialDeduction:
    def __init__(self, invoice_info, accident_no, deduction_amount, cookie):
        self.invoice_info = invoice_info
        self.accident_no = accident_no
        self.deduction_amount = deduction_amount
        self.cookie = cookie
        pass

    def get_object_id(self):
        for info in self.invoice_info:
            if info.get('accidentNo') == self.accident_no and info.get('deductibleAmount') == self.deduction_amount:
                return info.get('objectId')
        pass

    def get_deduction_params(self, rep_deduction):
        prplInvoiceReadyVOOldList = rep_deduction.get('prplInvoiceReadyVOOldList')[0]
        if prplInvoiceReadyVOOldList:
            deduction_result = copy.deepcopy(prplInvoiceReadyVOOldList)
            split = prplInvoiceReadyVOOldList['deductibleAmount'] / 2

            deduction_result['deductibleAmount'] = str(split)
            deduction_result['prplInvoiceReadyKindEOList'][0]['deductibleAmount'] = str(split)
            rep_deduction['prplInvoiceReadyVONewList'] = [deduction_result, deduction_result]
        return rep_deduction
        pass

    def get_body(self, rep_deduction, deductibleAmount, deductibleAmount2):
        prplInvoiceReadyVOOldList = rep_deduction.get('prplInvoiceReadyVOOldList')[0]
        if prplInvoiceReadyVOOldList:
            deduction_result = copy.deepcopy(prplInvoiceReadyVOOldList)
            deduction_result2 = copy.deepcopy(prplInvoiceReadyVOOldList)
            split = deductibleAmount
            split2 = deductibleAmount2

            deduction_result['deductibleAmount'] = str(split)
            deduction_result2['deductibleAmount'] = str(split2)
            deduction_result['prplInvoiceReadyKindEOList'][0]['deductibleAmount'] = str(split)
            deduction_result2['prplInvoiceReadyKindEOList'][0]['deductibleAmount'] = str(split2)
            rep_deduction['prplInvoiceReadyVONewList'] = [deduction_result, deduction_result2]
        return rep_deduction
        pass

    def partial_deduction(self, amount1, amount2):
        object_id = self.get_object_id()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Cookie': self.cookie
        }
        url_before_deduction = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/initInvoiceReadyPartSpiltDate?objectId={object_id}'
        session_ = requests.Session()
        rep_deduction = session_.post(url=url_before_deduction, headers=headers).json()
        rep_deduction_sort = {}
        rep_deduction_sort['prplInvoiceReadyVONewList'] = rep_deduction['prplInvoiceReadyVONewList']
        rep_deduction_sort['prplInvoiceReadyVOOldList'] = rep_deduction['prplInvoiceReadyVOOldList']

        # params_deduction = self.get_deduction_params(rep_deduction_sort)
        params_deduction = self.get_body(rep_deduction_sort, amount1, amount2)
        url_after_deduction = 'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/invoiceReadyPartSpilt?'  # 拆分保存链接，json参数为拆分的json
        rep_deduction = session_.post(url=url_after_deduction, headers=headers, json=params_deduction).json()
        print(rep_deduction)
        pass


# obj_query = QueryInvoiceReady("80052022220000025860,80052022220000023102,80052022220000024370,80052022220000026020,80052022220000023283")
# invoice_info, _, _ = obj_query.query_invoice_ready()
# obj_deduction = PartialDeduction(invoice_info=invoice_info, accident_no='80052022220000025860', deduction_amount=275)
# obj_deduction.partial_deduction(170, 105)
























# url_before_deduction =  'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/initInvoiceReadyPartSpiltDate?objectId=23872318044'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
# }
# session_ = requests.Session()
# rep = session_.post(url=url_before_deduction, headers=headers).json()
# print(rep)


# url_after_deduction = 'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/invoiceReadyPartSpilt?' # 拆分保存链接，params参数为拆分的json
# params = ''
# session_.post(url=url_after_deduction, headers=headers, params=params)
