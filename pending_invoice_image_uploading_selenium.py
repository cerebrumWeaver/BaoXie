import sys
import os
import copy
import threading
import time
import logging as log_

import pandas as pd
import requests
from webdriver_manager.chrome import ChromeDriverManager  # 三方库安装驱动

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from pending_invoice_fetch import PendingInvoiceFetch
from utils.log import Log


class PendingInvoiceImageUploadingSelenium:
    def __init__(self, packing_id, df=None, df2=None, cookie_uploading='', invoice_fileName='', invoice_path='', port=9523):
        if df is None:
            df = []
        if df2 is None:
            df2 = []
        if port is None:
            port = 9523
        self.packing_id = packing_id
        self.cookie_uploading = cookie_uploading
        self.invoice_path = invoice_path
        # self.invoice_fileName = invoice_fileName
        # self.invoice_fileName = f'D:\\000\\2023-05-26\\residue\\{invoice_fileName}'
        # self.invoice_fileName = \.path.join(os.path.join(os.path.join(f"D:\\000\\{time.strftime('%Y-%m-%d', time.localtime(time.time()))}", 'residue'), invoice_fileName))
        self.invoice_fileName = os.path.join(os.path.join(os.path.join(f"D:\\000\\{invoice_path}", 'residue'), invoice_fileName))
        self.service_ids = []
        self.service_id = None
        # 创建一个锁对象

        self.lock = threading.Lock()

        if len(df):
            print(f'df是否为空{len(df)}')
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
            if len(df) > 1:
                index = df[df.path.str.contains(invoice_fileName)].index
                self.invoiceNo = df.no[index].squeeze()
                self.invoiceCode = df.code[index].squeeze()
                self.billingDate = df.invoicedDate[index].squeeze()
                self.invoiceAmount = df.amount[index].squeeze()
                self.taxAmount = df.amountVat[index].squeeze()
                self.taxPayName = df['supplier.fullname'][index].squeeze()
                self.taxPayerNo = df['supplier.taxNo'][index].squeeze()
                self.buyTaxPayerName = df['branch.fullname'][index].squeeze()
                self.buyTaxPayerNo = df['branch.taxNo'][index].squeeze()
                self.invoiceRate = df.rateVat[index].squeeze()
                self.buyTaxPayerNameFace = self.buyTaxPayerName

                pass

        if len(df2):
            print(f'df2是否为空{len(df2)}')
            # 以下变量用于发票校验
            self.invoiceNo = df2.no.squeeze()  # 发票号
            self.invoiceCode = df2.code.squeeze()  # 发票代码
            self.billingDate = df2.invoicedDate.squeeze()  # 发票日期
            self.invoiceAmount = df2.amount.squeeze()  # # 发票金额（不含税）
            self.taxAmount = df2.amountVat.squeeze()  # 发票税额
            self.taxPayName = df2.originalSupplierName.squeeze()  # 销方名称
            self.taxPayerNo = df2.originalSupplierTaxNo.squeeze()  # 销方税号
            self.buyTaxPayerName = df2.branchFullName.squeeze()  # 购方名称
            self.buyTaxPayerNo = df2.branchTaxNo.squeeze()  # 购房税号
            self.invoiceRate = df2.rateVat.squeeze()  # 税率
            self.buyTaxPayerNameFace = self.buyTaxPayerName

        self.chromeOptions = ChromeOptions()
        self.chromeOptions.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        # self.chromeOptions.add_argument('--start-maximized')  # 最大化窗口
        self.chromeOptions.binary_location = "D:/chrome83/ChromePortable/App/Google Chrome/chrome.exe"  # 浏览器位置
        # self.chromeOptions.add_experimental_option('detach', True)  # 保持浏览器打开状态

        # 以最高权限运行，可以解决DevToolsActivePort文件不存在的报错
        self.chromeOptions.add_argument("--no-sandbox")
        # 最大化运行
        self.chromeOptions.add_argument("--start-maximized")
        # options.add_experimental_option('detach', True)  # 保持浏览器打开状态
        # 屏蔽--ignore-certificate-errors提示信息
        self.chromeOptions.add_argument("--ignore-certificate-errors")
        # 不加载GPU，规避bug
        self.chromeOptions.add_argument("--disable-gpu")
        self.chromeOptions.add_argument("--disable-software-rasterizer")
        # 禁用浏览器正在被自动化程序控制的提示
        self.chromeOptions.add_argument('--disable-infobars')

        # self.driver = webdriver.Chrome(options=self.chromeOptions, service=ChromeService(ChromeDriverManager().install()))
        self.driver = webdriver.Chrome(options=self.chromeOptions)

        self.driver.switch_to.new_window('tab')

        self.driver.implicitly_wait(10)  # 隐式等待
        pass

    def del_file(self, ):
        # 判断文件是否存在
        if os.path.exists(self.invoice_fileName):
            # 删除文件
            try:
                os.remove(self.invoice_fileName)
                pass
            except Exception as e:
                print(f'{self.invoice_fileName}文件被占用，删除失败，7s后再删除')
                log_.info(f'{self.invoice_fileName}文件被占用，删除失败，7s后再删除')
                time.sleep(7)
                try:
                    os.remove(self.invoice_fileName)
                    print(f'{self.invoice_fileName}文件被占用，尝试2次删除，已成功删除！')
                    log_.info(f'{self.invoice_fileName}文件被占用，尝试2次删除，已成功删除！')
                    pass
                except Exception as e:
                    print(f'{self.invoice_fileName}文件无法被删除')
                    log_.info(f'{self.invoice_fileName}文件无法被删除')
                    df = pd.DataFrame(data=[self.invoice_fileName + ' drop failure ' + str(self.packing_id)])
                    try:
                        with self.lock:
                            with open(os.path.join(f"D:\\000\\{self.invoice_path}", 'image_uploading.csv'), mode='a+', newline='') as f:
                                df.to_csv(f, index=False, header=False, )
                    except Exception as e:
                        pass
                pass
            else:
                print(f"{threading.current_thread().name}：文件{self.invoice_fileName}已成功删除！")
        else:
            print(f"{threading.current_thread().name}：文件{self.invoice_fileName}不存在，无法删除，请检查打包号{self.packing_id}影像上传图片是否全部成功。")
            df = pd.DataFrame(data=[self.invoice_fileName + ' nonexistence ' + str(self.packing_id)])
            try:
                with self.lock:
                    with open(os.path.join(f"D:\\000\\{self.invoice_path}", 'image_uploading.csv'), mode='a+', newline='') as f:
                        df.to_csv(f, index=False, header=False, )
            except Exception as e:
                pass

    def get_uploading_url(self, ):
        session_ = requests.Session()
        url_packing_info = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/queryPrpLInvoiceReadyList?batchNo={self.packing_id}'
        # Log()  # 初始化日志配置

        try:
            headers_ = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            }
            # rep = request(method='POST', url=url_, headers=headers_)
            packing_info = session_.post(url=url_packing_info, headers=headers_).json()

            headers_ = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                'cookie': self.cookie_uploading
            }

            for info in packing_info['prplInvoiceReadyEOList']:
                register_no = info['registNo']
                print(f'报案号：{register_no}')
                url_ = f'http://9.0.9.11/newclaimcar/controller/claim/prplinvoicedetailmain/prplInvoiceDetailMain/openImageByUrl?registNo={register_no}'
                rep = session_.post(url=url_, headers=headers_)
                if rep.ok:
                    self.uploading_image(rep.json())
                else:
                    log_.error(f'{threading.current_thread().name}：打包号{self.packing_id}下的报案号{register_no}接口请求异常，该报案号影像上传可能异常，请确认')
        except Exception as e:
            print(f'{threading.current_thread().name}：打包号{self.packing_id}影像上传接口异常：\n{e}')
            log_.critical(f'{threading.current_thread().name}：打包号{self.packing_id}影像上传接口异常：\n{e}')
            if self.service_id in self.service_ids:
                self.service_ids.remove(self.service_id)  # 发生了异常把业务号剔除
            time.sleep(1)
            self.get_uploading_url()
        else:
            print(f'{threading.current_thread().name}：打包号{self.packing_id}影像上传成功')
            log_.info(f'{threading.current_thread().name}：打包号{self.packing_id}影像上传成功')
            if self.invoice_fileName.split('.')[-1] != 'ofd':
                self.del_file()
            self.driver.close()
            # 切换回原来的浏览器窗口
            self.driver.switch_to.window(self.driver.window_handles[0])
            try:
                self.submit_selenium()
            except Exception as e:
                # 校验失败：需要关闭 打包发票处理tab
                # 关闭 打包发票处理tab
                self.driver.switch_to.default_content()  # 重置 打包发票处理tab iframe
                close_pending_invoice_xpath = '//*[@id="tabControl"]/nav/tabs/tab[4]/div[2]/i'
                close_pending_invoice_element = WebDriverWait(self.driver, 30, 0.5).until(EC.presence_of_element_located(('xpath', close_pending_invoice_xpath)))
                close_pending_invoice_element.click()
                df = pd.DataFrame(data=[self.packing_id])
                print('最外层异常执行了')
                with self.lock:
                    with open(os.path.join(f"D:\\000\\{self.invoice_path}", 'packing_id.csv'), mode='a+', newline='') as f:
                        df.to_csv(f, index=False, header=False,)
                # df.to_csv(r"D:\000\uncommitted_packing_id\packing_id.csv", index=False, header=False, mode='a+')
                print(f'{threading.current_thread().name}：submit_selenium函数异常！！！请手动提交打包号{self.packing_id}')
                log_.info(f'{threading.current_thread().name}：submit_selenium函数异常！！！请手动提交打包号{self.packing_id}')
                pass

        pass

    def uploading_image(self, url):
        self.driver.get(url)
        time.sleep(2.5)
        # -------------------------------------------START----------------------------------------
        # 归类后立即上传
        xpath01 = '/html/body/div[1]/div[1]/div[2]/section/div/div/div[2]/div[1]/form/div[2]/div[5]/span'
        element01 = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', xpath01)))
        element01.click()

        xpath_text = '/html/body/div[1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/div/div'
        element_text = WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(('xpath', xpath_text)))
        while not element_text.text:
            pass
        self.service_id = element_text.text

        # -------------------------------------------END----------------------------------------

        if self.service_id not in self.service_ids:
            # self.service_ids.append(self.service_id)
            print(f'{threading.current_thread().name}：事故号{self.service_id}开始影像上传')
            # -------------------------------------------START(实物赔付修理三方协议)----------------------------------------
            # 车险理赔-赔款抵扣税单证
            xpath02 = '/html/body/div[1]/div[1]/div[1]/div[3]/div[2]/div[2]/div[3]/ul/li[21]/a/span[1]'
            element02 = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', xpath02)))
            element02.click()

            # 实物赔付修理三方协议
            xpath03 = '/html/body/div[1]/div[1]/div[1]/div[3]/div[2]/div[2]/div[3]/ul/li[24]/a/span[1]'
            element03 = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', xpath03)))
            element03.click()
            # -------------------------------------------END(实物赔付修理三方协议)----------------------------------------

            file02 = self.driver.find_element(by=By.XPATH, value='//*[@id="file-fr"]')  # 选择文件上传
            file02.send_keys(self.invoice_fileName)
            time.sleep(2.5)
            self.service_ids.append(self.service_id)
        else:
            print(f'{threading.current_thread().name}：事故号{self.service_id}已经上传，无需再上传')
            pass
        pass

    def submit_selenium(self):
        self.driver.switch_to.default_content()  # 重置 任务管理tab iframe
        self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[3]/c-iframe/iframe'))  # 定位 任务管理 iframe

        # 定位 发票打包号文本框
        # text_frame_element = self.driver.find_element(by=By.XPATH, value='//*[@id="invoiceBatchQueryCar"]/div[1]/c-query-form/fields[1]/field[1]/c-input/input')
        # time.sleep(0.5)
        # text_frame_element.clear()
        # time.sleep(0.5)
        # text_frame_element.send_keys(self.packing_id)

        # 定位 发票打包号文本框
        text_frame_xpath = '//*[@id="invoiceBatchQueryCar"]/div[1]/c-query-form/fields[1]/field[1]/c-input/input'
        text_frame_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', text_frame_xpath)))
        # text_frame_element = self.driver.find_element(by=By.XPATH, value='//*[@id="invoiceBatchQueryCar"]/div[1]/c-query-form/fields[1]/field[1]/c-input/input')
        while text_frame_element.get_attribute('value') != self.packing_id:
            text_frame_element.clear()
            time.sleep(1)
            text_frame_element.send_keys(self.packing_id)

        # 点击 查询
        self.driver.find_element(by=By.XPATH, value='//*[@id="invoiceBatchQueryCar"]/div[1]/c-query-form/fields[4]/c-button[1]/span').click()
        # 定位 处理 跳到 打包发票处理tab
        self.driver.find_element(by=By.XPATH, value='//*[@id="invoiceBatchQueryCar"]/div[1]/div/c-table/div[1]/div[2]/ul/div/cell[1]/div/div/a[1]').click()

        self.driver.switch_to.default_content()  # 重置 打包发票处理tab iframe
        self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[4]/c-iframe/iframe'))  # 定位 打包发票处理tab iframe
        self.driver.find_element(by=By.XPATH, value='//*[@id="invoiceDate"]/span').click()  # 点击 发票登记

        if self.invoice_fileName.split('.')[-1] == 'ofd':
            # 点击下拉小三角
            self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[1]/field/c-dropdown/i[1]').click()
            # time.sleep(0.5)
            tax_selector_xpath = '/html/body/div[3]/div/c-listview/ul/li[2]'
            WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', tax_selector_xpath))).click()    # 点击电子发票选项

            electronic_invoice_xpath = '//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[1]/field/c-button/span'
            WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', electronic_invoice_xpath))).click()  # 点击 电子发票 签名按钮 来 上传发票

            # xpath = '//*[@id="rt_rt_1h39k6f2n1osd1iv81r3oru1te71"]/input'
            # xpath = '//*[@id="rt_rt_1h39kv4cp4391ibr1tf51po81fqi1"]/input'
            # xpath = '/html/body/c-uploader-sidebar/c-uploader/c-subview/div[1]/v-box/flex-box/div[1]/div[2]/div[2]/input'
            xpath = '//input[@type="file"]'
            WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', xpath))).send_keys(self.invoice_fileName)    # 上传发票
            time.sleep(2.5)
            close_xpath = '/html/body/div[6]/div/div[3]/div[3]/span'
            WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', close_xpath))).click()   # 关闭弹窗
            self.del_file()     # 删除ofd文件

            pass
        else:
            # 此处选择发票类型
            self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[1]/field/c-dropdown/i[1]').click()
            tax_selector_xpath = '/html/body/div[3]/div/c-listview/ul/li[1]'
            WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', tax_selector_xpath))).click()    # 点击增值税发票
            pass

        # 发票号码
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[1]/c-input/input').send_keys(self.invoiceNo)

        # 发票代码
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[2]/c-input/input').send_keys(self.invoiceCode)

        # 开票日期
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[3]/c-datepicker/input').send_keys(self.billingDate)

        # 发票金额不含税
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[4]/c-input/input').send_keys(self.invoiceAmount)

        # 税率
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[5]/c-input/input').send_keys(self.invoiceRate)

        # 税额
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[6]/c-input/input').send_keys(self.taxAmount)


        # 销方纳税人名称
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[7]/c-input/input').send_keys(self.taxPayName)

        # 销方纳税人识别号
        taxPayerNo_element = self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[8]/c-input/input')
        taxPayerNo_element.send_keys(self.taxPayerNo)

        # 购方纳税人名称
        select_element = self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[10]/c-dropdown/input')
        while True:
            if select_element.get_attribute('value') != self.buyTaxPayerName:
                select_element.clear()
                taxPayerNo_element.click()
                select_element.click()
                select_element.send_keys(self.buyTaxPayerName)
                # select_element.send_keys('中国人寿财产保险股份有限公司玉树州中心支公司')
                time.sleep(0.5)
                # 因为是个选择框，所以还要点击一下
                select_prompt_xpath = '/html/body/div[5]/div/c-listview/ul/li'
                try:
                    select_prompt_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', select_prompt_xpath)))
                    select_prompt_element.click()
                except Exception as e:
                    print('购方纳税人名称录入错误，跳出本轮循环从新继续')
                    continue
                pass
            else:
                break

        # # 购方纳税人识别号
        # self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[11]/c-input/input').send_keys(self.invoiceNo)

        # 购方纳税人名称（票面）
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[2]/div/div/c-query-form[1]/fields[2]/field[17]/c-input/input').send_keys(self.buyTaxPayerNameFace)
# --------------------------------------------------------------------------------------输入结束-------------------------------------------------------------------------------

        # 点击 发票校验
        self.driver.find_element(by=By.XPATH, value='//*[@id="_id64"]/div[1]/div/div[1]/div/div/c-button[1]/span').click()

        # verify_text_xpath = '/html/body/div[5]/div/div[2]/div[2]'
        verify_text_xpath = '/html/body/div[6]/div/div[2]/div[2]'
        # verify_text_xpath = '/html/body/div[6]/div/div[3]/div[3]/span'
        verify_text_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', verify_text_xpath)))
        verify_text = verify_text_element.text
        # verify_text = self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/div[2]/div[2]').text
        if verify_text == '通过校验！':
            self.driver.find_element(by=By.XPATH, value='/html/body/div[6]/div/div[3]/div[3]/span').click()  # 关闭 通过校验 弹窗
            self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[1]/c-navbar/div/nav/c-menu/div[2]/a[4]/span').click()  # 点击 提交
            # 添加等待时间
            submit_text_xpath = '/html/body/div[5]/div/div[2]/div[2]'
            submit_text_element = WebDriverWait(self.driver, 60, 0.5).until(EC.presence_of_element_located(('xpath', submit_text_xpath)))
            while not submit_text_element.text:
                pass
            if submit_text_element.text == '登记成功！该打包任务满足自动审核规则，请确认是否自动审核通过？':
                self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/div[3]/div[2]/span').click()  # 点击 确认 消除弹窗后 打包发票处理tab 变成 待开发票打包tab
                # time.sleep(1)

                # 关闭 待开发票打包tab
                close_pending_invoice_xpath = '//*[@id="tabControl"]/nav/tabs/tab[4]/div[2]'
                close_pending_invoice_element = WebDriverWait(self.driver, 30, 0.5).until(EC.presence_of_element_located(('xpath', close_pending_invoice_xpath)))
                close_pending_invoice_element.click()
            else:
                # 提交失败：需要关闭 打包发票处理tab
                # 关闭 打包发票处理tab
                self.driver.switch_to.default_content()  # 重置 打包发票处理tab iframe
                close_pending_invoice_xpath = '//*[@id="tabControl"]/nav/tabs/tab[4]/div[2]/i'
                close_pending_invoice_element = WebDriverWait(self.driver, 30, 0.5).until(EC.presence_of_element_located(('xpath', close_pending_invoice_xpath)))
                close_pending_invoice_element.click()

                df = pd.DataFrame(data=[self.packing_id])
                with self.lock:
                    with open(os.path.join(f"D:\\000\\{self.invoice_path}", 'packing_id.csv'), mode='a+', newline='') as f:
                        df.to_csv(f, index=False, header=False,)
                # df.to_csv(r"D:\000\uncommitted_packing_id\packing_id.csv", index=False, header=False, mode='a+')
                print(f'{threading.current_thread().name}：校验成功，但提交后弹窗无法关闭！！！请手动提交打包号{self.packing_id}')
                log_.info(f'{threading.current_thread().name}：校验成功，但提交后弹窗无法关闭！！！请手动提交打包号{self.packing_id}')
                pass
        else:
            # 校验失败：需要关闭 打包发票处理tab
            # 关闭 打包发票处理tab
            self.driver.switch_to.default_content()  # 重置 打包发票处理tab iframe
            close_pending_invoice_xpath = '//*[@id="tabControl"]/nav/tabs/tab[4]/div[2]/i'
            close_pending_invoice_element = WebDriverWait(self.driver, 30, 0.5).until(EC.presence_of_element_located(('xpath', close_pending_invoice_xpath)))
            close_pending_invoice_element.click()

            df = pd.DataFrame(data=[self.packing_id])
            with self.lock:
                with open(os.path.join(f"D:\\000\\{self.invoice_path}", 'packing_id.csv'), mode='a+', newline='') as f:
                    df.to_csv(f, index=False, header=False, )
            # df.to_csv(r"D:\000\uncommitted_packing_id\packing_id.csv", index=False, header=False, mode='a+')
            print(f'{threading.current_thread().name}：校验失败！！！请手动提交打包号{self.packing_id}')
            log_.info(f'{threading.current_thread().name}：校验失败！！！请手动提交打包号{self.packing_id}')

        pass

# # -------------------------------------------取消注释--------------------------------------------------------------------------


if __name__ == '__main__':
    data_claimNos, data_invoices, supplierName, claims_rule = PendingInvoiceFetch().fetch_invoice()

    df_verification = pd.json_normalize(data_invoices)

    invoice_number_s = []
    for data_invoice in data_invoices:
        # 提取发票文件名称 和 时间 路径（"/invoice/中国人寿财产保险股份有限公司长春中心支公司/2023-05-04/赔款/发票4816.jpg"）
        invoice_number_s.append((data_invoice['amountTotal'], data_invoice['path'].split('/')[-1], data_invoice['path'].split('/')[-3]))
    df_invoice_number_s = pd.DataFrame(sorted(invoice_number_s, reverse=True))
    invoice_s = copy.deepcopy(df_invoice_number_s)
    for i in range(len(invoice_s)):


        # obj = PendingInvoiceImageUploadingSelenium('V66572023330100011301', df=df_verification,
        #                                            cookie_uploading='SESSION=b93a42ff-f135-474c-8372-a37011924d35; _pk_id.18.92e3=1d96324aa15db994.1684389912.; _pk_ses.18.92e3=1; SESSION=31e57091-d6af-4f23-a1ce-751b31bd828c; BIGipServerNCS_Nginx_P80=!NGyrwPrk3ZapDr1lxDsjQ5eIaE4M2XL9W12V4x7G3mopRgSSUSnae6Ak3NEOMWTNqPk7C5FT1E9FefA=; UAMSessionID=ADCE3A395CBB670C827D3987EC4A8547.instance-141-48; UAMAuth=89979dc67155bfc901719aa0f11d1740; UAMauthentication=073e5480-6ddc-4c30-9548-519edf71c919; BIGipServerPool_SHDC_Portol_Auth2=!1sNpI5Qu6+aJWC+L3UZgqG4W5Y/lOfHqTojgjOWQ4xE3hwETUQneaBWPe9KrPr4PlMilEGC7O5Z9QA==; BIGipServerPool_Matomo_T033_P8000=!UYHNfPzuXoHsG75lxDsjQ5eIaE4M2SmYJme4IS9Xp1ZChYLASBkKgB0cBbCfAWODmwVCNy+4Pk/u8VA=; BIGipServerPool_NewClaimCounter_P7001=3573813257.22811.0000',
        #                                            invoice_fileName='test.jpg', invoice_path='2023-06-08')\
        packing_id_str = input('请输入打包号：\n')
        obj = PendingInvoiceImageUploadingSelenium(packing_id_str, df=df_verification,
                                                   cookie_uploading='SESSION=a12f3a51-1758-4635-b3e3-1cc73a83928f; _pk_ses.18.92e3=1; _pk_id.18.92e3=1d96324aa15db994.1684389912.; BIGipServerPool_SHDC_Portol_Auth2=!znfUyIA7yktil3SL3UZgqG4W5Y/lOZMSBG9pa09ajfLDjtOJ207d9dy3Ql0IB6Y3+Ci7c82osx6ZVg==; SESSION=a2dbd824-768b-456a-930f-5d1bca19ea9c; UAMSessionID=CD0196AB1FCF85FA7A2F05058585543D.instance-141-48; BIGipServerNCS_Nginx_P80=!EPxgZYcS8BdwIvhlxDsjQ5eIaE4M2QJ6zw7bV0Y/YzjG9hTnzOQEQ4h0rsWaKtyVk0ud0gh33ygca3Y=; BIGipServerPool_Matomo_T033_P8000=!I6P/D4mCTh55HCFlxDsjQ5eIaE4M2Z6fOav3WkTqHCcVNqGnftx6UPfpqZX/J6qTpFmOr8o1jynOfjw=; UAMAuth=89979dc67155bfc901719aa0f11d1740; UAMauthentication=1983d4c2-ecef-4b24-bfab-397ce9b33302; BIGipServerPool_NewClaimCounter_P7001=3372486665.22811.0000',
                                                   invoice_fileName=invoice_s[1].values.tolist()[i], invoice_path=invoice_s[2].values.tolist()[i])
        obj.get_uploading_url()
# # ---------------------------------------------------------------------------------------------------------------------------

# 80052023330000084072,80052023330000112592,80052023330000112592,80052023330000104534,80052023330000051745,80052023330000051745(有问题的接口方式提交)
