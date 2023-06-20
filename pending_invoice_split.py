import copy
import numpy as np
import pandas as pd
from partial_deduction import PartialDeduction
from pending_invoice_fetch import PendingInvoiceFetch
from pending_invoice_inquiry import PackInvoice
from utils.log import LogUru
from utils.log import Log
import logging as log_


class DeductionSplit:
    def __init__(self, session, invoice_s, accident_no, df_verification_, cookie_packing, port):
        self.session = session
        self.invoice_s = invoice_s[0].values.tolist()
        self.invoice_fileName = invoice_s[1].values.tolist()
        self.invoice_path = invoice_s[2].values.tolist()
        self.accident_no = accident_no
        self.df_verification = df_verification_
        self.cookie_packing = cookie_packing
        self.port = port
        Log()

# 此方法经过split_pack方法优化
    def invoice_split_pack(self, obj_query, fields, invoices):
        if round(fields.deductibleAmount.sum(), 4) == round(sum(invoices), 4):
        # if fields.deductibleAmount.sum() == sum(invoices):
            # for invoice in sorted(self.invoice_s, reverse=True):
            for index, invoice in enumerate(self.invoice_s):
                fields.sort_values(by='deductibleAmount', ascending=False, inplace=True)
                fields['cum_sum'] = fields.deductibleAmount.cumsum()
                # 获取拆分的项事故号
                split_fields = fields[fields.cum_sum >= invoice].head(1)    # 获取拆分的项
                accident_no_ = split_fields.accidentNo.values.tolist()[0]
                paid_amount_ = split_fields.paidAmount.values.tolist()[0]
                deductible_amount_ = split_fields.deductibleAmount.values.tolist()[0]
                residue_deductible_amount = split_fields.cum_sum.values.tolist()[0] - invoice
                fields_lt = fields[~(fields.cum_sum >= invoice)]
                fields_lt_et = fields[~(fields.cum_sum > invoice)]

                print('*' * 100)

                print(f'\n打包objectID信息：\n{pd.concat([fields_lt, split_fields])}\n待打包objectID剩余总金额：{fields.deductibleAmount.sum()}')

                print(f'\n当前打包发票金额为：{invoice}，发票剩余总金额：{sum(invoices)}')

                # 删除待打包的objectID
                object_id_list = fields_lt.objectId.values.tolist()
                accident_no_list = fields_lt.accidentNo.values.tolist()
                object_id_list_lt_et = fields_lt_et.objectId.values.tolist()

                if residue_deductible_amount:
                    # # 删除待打包的objectID
                    # object_id_list = fields[~(fields.cum_sum >= invoice)].objectId.values.tolist()
                    print('拆分。。。')
                    need_deduction_amount = deductible_amount_ - residue_deductible_amount

                    # 初始化拆分类
                    obj_deduction = PartialDeduction(invoice_info=obj_query.query_invoice_ready()[0], accident_no=accident_no_, deduction_amount=deductible_amount_, cookie=self.cookie_packing)
                    obj_deduction.partial_deduction(need_deduction_amount, residue_deductible_amount)

                    # 拆分后 再查询
                    query_info = obj_query.query_invoice_ready()[0]

                    # 获取need_deduction_amount打包id
                    object_id_ = self.get_object_id(query_info, accident_no_, need_deduction_amount, fields)
                    print(f'object_id_值：{object_id_}')
                    # 获取residue_deductible_amount打包id
                    object_id_residue = self.get_object_id(query_info, accident_no_, residue_deductible_amount, fields)
                    object_id_list.append(object_id_)
                    while None in object_id_list:
                        object_id_list.remove(None)
                        print('if语句删除了object_id_list中的None值')
                    accident_no_list.append(accident_no_)
                    self.accident_no = ','.join(accident_no_list)

                    fields.drop(split_fields.index, inplace=True)
                    fields.drop(fields_lt_et.index, inplace=True)
                    if len(fields.index):
                        # ValueError: max() arg is an empty sequence
                        fields.loc[max(fields.index) + 1] = [object_id_residue, accident_no_, paid_amount_, residue_deductible_amount, None]  # 添加 事故号减发票金额
                    else:
                        fields.loc[0] = [object_id_residue, accident_no_, paid_amount_, residue_deductible_amount, None]
                else:
                    print('无需拆分。。。')
                    object_id_list = object_id_list_lt_et
                    while None in object_id_list:
                        object_id_list.remove(None)
                        print('else语句删除了object_id_list中的None值')
                    fields.drop(fields_lt_et.index, inplace=True)
                    pass
                # 打包代码
                obj_pack = PackInvoice(accident_no=self.accident_no, df_verification=self.df_verification, cookie_packing=self.cookie_packing)
                obj_pack.start_packing(self.session, map(lambda x: str(x), object_id_list), self.invoice_fileName[index], self.invoice_path[index], port=self.port)
                invoices.remove(invoice)
        else:
            print(f'事故号 {self.accident_no} 打包总金额不等于发票总金额')
        return fields, invoices
        pass

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


# ----------------------------------------------以下 全部取消注释测试-------------------------------------------------
if __name__ == '__main__':
    while True:
        # invoice_number_s = [7719]
        invoice_number_s = [2100]
        accidentNo = "80052023330000116611"
        # accidentNo = "80052022220000025860,80052022220000023102,80052022220000024370,80052022220000026020,80052022220000023283"
        # accidentNo = "80052022220000022822,80052022220000026590,80052022220000026507,80052022220000023349,80052022220000023349,80052022220000023864,80052022220000026590,80052022220000026590,80052022220000016204"

        data_claimNos, data_invoices, supplierName, claims_rule = PendingInvoiceFetch().fetch_invoice()    # 有数据时取消注释

        accidentNo = data_claimNos
        invoice_number_s = []

        # invoice_number_s = [4816]
        for data_invoice in data_invoices:
            # 提取发票文件名称 和 时间 路径（"/invoice/中国人寿财产保险股份有限公司长春中心支公司/2023-05-04/赔款/发票4816.jpg"）
            invoice_number_s.append((data_invoice['amountTotal'], data_invoice['path'].split('/')[-1], data_invoice['path'].split('/')[-3]))

        df_invoice_number_s = pd.DataFrame(sorted(invoice_number_s, reverse=True))

        # 初始化查询类
        from pending_invoice_inquiry import QueryInvoiceReady
        objQuery = QueryInvoiceReady(accident_no=accidentNo, accountName=supplierName)  # accountName='浙江元祺汽车有限公司'
        invoiceInfo, Session_, _ = objQuery.query_invoice_ready()
        if not invoiceInfo:
            print(f'\n事故号查询为空，当心已经打包过造成无法查询！！！跳过本轮后续程序，请核对事故号：{accidentNo}')
            continue

        df_verification = pd.json_normalize(data_invoices)
        # 初始化发票金额（copy.deepcopy(pd.DataFrame([(9000, 'merge9000.jpg'), (1506, 'merge1506.jpg')]))）
        obj_deduction_split = DeductionSplit(Session_, copy.deepcopy(df_invoice_number_s), accident_no=accidentNo, df_verification_=df_verification,
                                             cookie_packing='SESSION=ae941955-89f2-4233-89e0-86943aa654f6; _pk_ses.18.92e3=1; _pk_id.18.92e3=1d96324aa15db994.1684389912.; BIGipServerPool_SHDC_Portol_Auth2=!7SmFiiKnNQJwMdOL3UZgqG4W5Y/lOeImsKBRvmFjGFmh+3Inz0JfT6rm0VrrYS0WxwHBrpsrowY2Hw==; SESSION=f01c38da-af6e-4f1c-816b-7f71edcb8d5e; UAMSessionID=AF0903F4519FEA3A882CC247A0F8B8D3.instance-141-47; JSESSIONID=57F5FB2EC3BD55B7641C261814ED63D1.instance-164-119; BIGipServerNCS_Nginx_P80=!McHZirdAqV/hCxZlxDsjQ5eIaE4M2VxcezDvArsVbLER51/uIF1o/H7PnuPb0Tqmx/D7OtWYqfF/DhA=; UAMAuth=89979dc67155bfc901719aa0f11d1740; UAMauthentication=cfd17de3-7061-4312-bc61-56e16c814796; BIGipServerPool_NewClaimCounter_P7001=3640922121.22811.0000',
                                             port=9523)
        df_deduction = pd.json_normalize(invoiceInfo)[['objectId', 'accidentNo', 'paidAmount', 'deductibleAmount']]
        # df_deduction_rule = pd.json_normalize(invoiceInfo)[['accidentNo', 'deductibleAmount', 'certiNo']]
        df_deduction_rule = pd.json_normalize(invoiceInfo)[['deductibleAmount', 'accidentNo', 'certiNo']]
        df_claims_rule = pd.DataFrame(claims_rule)
        if round(sum(df_invoice_number_s[0].values.tolist()), 4) < round(df_deduction.deductibleAmount.sum(), 4):
        # if sum(df_invoice_number_s[0].values.tolist()) < df_deduction.deductibleAmount.sum():
            # df_deduction.sort_values(by='deductibleAmount', ascending=False, inplace=True)
            # df_deduction = df_deduction[df_deduction_rule.isin({'accidentNo': df_claims_rule[1].values, 'deductibleAmount': df_claims_rule[0].values, 'certiNo': df_claims_rule[2].values}).all(axis=1)]
            df_deduction = df_deduction[df_deduction_rule.apply(lambda df: df.values.tolist() in (df_claims_rule.values.tolist()), axis=1)]
            if not df_deduction.values.tolist():
                accidentNo__ = accidentNo.replace(',', '\n')
                print(f'\n当心已经打包过造成无法打包或查询，请核对事故号：{accidentNo__}\n')
                log_.info(f'当心已经打包过造成无法打包或查询，请核对事故号：\n{accidentNo__}\n')
                continue
            pass

        Fields, Invoices = obj_deduction_split.invoice_split_pack(objQuery, df_deduction, invoices=df_invoice_number_s[0].values.tolist())





