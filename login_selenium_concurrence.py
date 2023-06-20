import os
import time
import queue
import threading
import copy
import pandas as pd
import logging as log_

from webdriver_manager.chrome import ChromeDriverManager  # 三方库安装驱动
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from requests import utils
from DynamicCode import dynamicCode
from utils.log import Log
from pending_invoice_fetch import PendingInvoiceFetch


class LoginSelenium:
    def __init__(self, login_url='', username='', password='', port=0):
        Log()  # 初始化日志配置
        self.login_url = login_url
        self.username = username
        self.password = password
        self.port = port

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
        self.driver.implicitly_wait(10)  # 隐式等待
        self.login_page()
        self.query_pending_invoice_packing()
        self.cookie_query, self.cookie_jar_query = self.query_pending_invoice_packing_cookies()
        self.task_processing_tab()  # 打开 任务处理tab
        print('Stop...')
        print('Stop...')
        print('Stop...')
        print(f'线程{threading.current_thread().name}已启动')
        log_.info(f'线程{threading.current_thread().name}已启动')
        self.consumer()
        pass

    def login_page(self):
        self.driver.get(self.login_url)
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div/span').click()
        self.driver.find_element(by=By.XPATH, value='//*[@id="userName"]').send_keys(self.username)
        self.driver.find_element(by=By.XPATH, value='//*[@id="userPwd"]').send_keys(self.password)
        self.driver.find_elements(by=By.XPATH, value='//*[@id="weiXinCode"]')[0].send_keys(dynamicCode().getDynamicCode('330102199902143023'))
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[2]/c-button[1]/span').click()   # 登录

        try:
            self.driver.find_element(by=By.XPATH, value='/html/body/div[4]/div/div[3]/div[2]').click()
        except Exception as e:
            log_.info("未显示弹窗：’您已在其他地方登录，是否强制登录？‘")
        time.sleep(3)

        # self.driver.find_element(by=By.XPATH, value='//*[@id="selectStructure"]/i[1]').click()  # 登录机构（点击下拉框）：杭州理赔/客服分中心
        WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located(('xpath', '//*[@id="selectStructure"]/i[1]'))).click()  # 登录机构（点击下拉框）：杭州理赔/客服分中心

        print(self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[1]').text)
        if self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[1]').text == '杭州理赔/客服分中心':
            self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[1]').click()
        else:
            self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[2]').click()
        self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[3]/c-button').click()  # 点击确定按钮取消弹窗
        time.sleep(5)
        log_.info('登录成功！！！')
        return self.driver
        pass

    def query_pending_invoice_packing(self,):
        try:
            # element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/c-button')))
            # element.click()

            self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="contentIframe"]/iframe'))     # 定位 主页 iframe
            self.driver.find_element(by=By.XPATH, value='//*[@id="carousel1"]/div[2]/div[1]/li[9]').click()  # 点击 待开发票打包

            self.driver.switch_to.default_content()  # 重置iframe
            self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[2]/c-iframe/iframe'))  # 定位 待开发票打包 iframe
            self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[3]/field[3]/c-input/input').send_keys('公主岭市吉洋名车维修服务中心2')  # 支付账户名称
            self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[9]/c-button[1]').click()  # 查询按钮
            log_.info('首次登录后，待开发票条件查询成功！！！')

        except Exception as e:
            # # 原始人脸验证部分 start（可取消注释复原）
            # self.driver.find_element(by=By.XPATH, value='//*[@id="facelog"]/div[2]/div/div/div/c-button/span').click()
            # self.driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[3]/div[3]/span').click()
            # print(f'请联系客户人脸验证')
            # log_.critical(f'请联系客户人脸验证：\n{e}')
            # time.sleep(10)
            # return self.query_pending_invoice_packing()
            # # 原始人脸验证部分 end（可取消注释复原）
            self.driver.switch_to.default_content()     # 重置iframe
            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[2]/img[2]').click()  # 点击符号：>
            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[1]/ul/li[9]/span').click()  # 点击 待开发票打包
            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div[1]/span').click()  # 回到符号：>页面
            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[2]/img[2]').click()  # 点击符号：>
            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[1]/ul/li[12]/span').click()  # 点击 任务处理
            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div[2]/i').click()  # 关闭符号：>页面

            self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div[1]/span').click()  # 点击 待开发票打包tab
            self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[2]/c-iframe/iframe'))  # 定位 待开发票打包 iframe
            self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[3]/field[3]/c-input/input').send_keys('公主岭市吉洋名车维修服务中心2')  # 支付账户名称
            self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[9]/c-button[1]').click()  # 查询按钮
            log_.info('首次登录后，待开发票条件查询成功！！！')

        else:
            return self.driver
        pass

    def query_pending_invoice_packing_cookies(self):
        query_cookies = self.driver.get_cookies().copy()
        cookies_list = []
        for query_cookie in query_cookies:
            cookies_list.append('{}={}'.format(query_cookie['name'], query_cookie['value']))
        cookie_selenium = '; '.join(cookies_list)
        # log_.info(f'selenium操作待开发票查询cookie信息：\n{cookie_selenium}\n{"——" * 50}')
        cookie = '; '.join(reversed(cookies_list))
        # target_cookies = []
        # index = [10, 8, 9, 6, 3, 5, 2, 1, 7, 4, 0]
        # for i in index:
        #     target_cookies.append(cookies_list[i])
        # cookie = '; '.join(target_cookies)
        # print(cookie)
        # log_.info(f'待开发票打包查询响应cookie信息：\n{cookie}\n{"——"*50}')
        cookie_dict = dict([c.split('=', 1) for c in cookie.split('; ')])
        cookie_jar = utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
        log_.info(f'selenium操作待开发票查询cookie信息：\n{cookie}\n{"——" * 50}')
        return cookie, cookie_jar
        pass

    def task_processing_tab(self):
        # self.driver.find_element(by=By.XPATH, value='/html/body/div[3]/div/div[3]/div[3]/span').click()  # 关闭 查询为空 弹窗
        dialog_xpath = '/html/body/div[3]/div/div[3]/div[3]/span'
        dialog_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', dialog_xpath)))
        dialog_element.click()

        # self.driver.switch_to.default_content()  # 重置iframe
        # home_xpath = '//*[@id="tabControl"]/nav/tabs/tab[1]/div/span'
        # home_element = WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located(('xpath', home_xpath)))
        # home_element.click()
        #
        # self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="contentIframe"]/iframe'))  # 定位 主页 iframe
        # self.driver.find_element(by=By.XPATH, value='//*[@id="carousel1"]/div[2]/div[1]/li[12]').click()  # 点击 任务管理 跳到 任务管理tab

        self.driver.switch_to.default_content()  # 重置iframe
        task_processing_xpath = '//*[@id="tabControl"]/nav/tabs/tab[3]/div[1]/span'
        task_processing_element = WebDriverWait(self.driver, 20, 0.5).until(EC.presence_of_element_located(('xpath', task_processing_xpath)))
        task_processing_element.click()

        self.driver.switch_to.default_content()  # 重置 任务管理tab iframe
        self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[3]/c-iframe/iframe'))  # 定位 任务管理 iframe

        advanced_query_xpath = '/html/body/div[1]/flex-box/div/c-panel/div[4]/c-query-form/fields[2]/field/c-button/span'
        advanced_query_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', advanced_query_xpath)))
        advanced_query_element.click()  # 点击 高级查询

        # 点击 发票处理
        # self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/flex-box/div/c-panel/div[4]/c-query-form/fields[3]/field/c-select-button-split/c-button[4]/span').click()
        # 上一行代码报元素不可交互错误
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/flex-box/div/c-panel/div[4]/c-query-form/fields[3]/field/c-select-button-split/c-button[4]/span"))).click()
        time.sleep(2)

    # 消费者（从先进先出队列Queue中消费数据）
    def consumer(self):
        while True:
            data_claimNos, data_invoices, supplierName, claims_rule = q.get()
            invoice_number_s = []
            for invoice in data_invoices:
                invoice_number_s.append((invoice['amountTotal'], invoice['path'].split('/')[-1], invoice['path'].split('/')[-3]))

            df_invoice_number_s = pd.DataFrame(sorted(invoice_number_s, reverse=True))
            # 初始化查询类
            from pending_invoice_inquiry import QueryInvoiceReady
            objQuery = QueryInvoiceReady(accident_no=data_claimNos, accountName=supplierName)
            invoiceInfo, Session_, _ = objQuery.query_invoice_ready()
            if not invoiceInfo:
                print('\n事故号查询为空，当心已经打包过造成无法查询！！！跳过本轮后续程序')
                continue

            # 初始化拆分发票金额
            from pending_invoice_split import DeductionSplit
            obj_deduction_split = DeductionSplit(session=Session_, invoice_s=copy.deepcopy(df_invoice_number_s), accident_no=data_claimNos, df_verification_=pd.json_normalize(data_invoices), cookie_packing=self.cookie_query, port=self.port)
            df_deduction = pd.json_normalize(invoiceInfo)[['objectId', 'accidentNo', 'paidAmount', 'deductibleAmount']]

            df_deduction_rule = pd.json_normalize(invoiceInfo)[['deductibleAmount', 'accidentNo', 'certiNo']]
            df_claims_rule = pd.DataFrame(claims_rule)
            if round(sum(df_invoice_number_s[0].values.tolist()), 4) < round(df_deduction.deductibleAmount.sum(), 4):
                df_deduction = df_deduction[df_deduction_rule.apply(lambda df: df.values.tolist() in (df_claims_rule.values.tolist()), axis=1)]
                if not df_deduction.values.tolist():
                    print('\n事故号查询为空，当心已经打包过造成无法查询！！！')
                    accidentNo__ = data_claimNos.replace(',', '\n')
                    log_.info(f'事故号查询为空，当心已经打包过造成无法查询，请核对事故号：\n{accidentNo__}\n')
                    continue
                pass
            _, _ = obj_deduction_split.invoice_split_pack(objQuery, df_deduction, invoices=df_invoice_number_s[0].values.tolist())
            print(f'事故号：\t{data_claimNos} 核销完毕！！！')
            q.task_done()   # 表示前面排队的任务已经被完成。被队列的消费者线程使用。每个 get() 被用于获取一个任务， 后续调用 task_done() 告诉队列，该任务的处理已经完成。


print('主线程开始')
q = queue.Queue(maxsize=10)


# 生产者（从保携后台拿数据，放入先进先出队列Queue中）
def producer():
    while True:
        data_claimNos, data_invoices, supplierName, claims_rule = PendingInvoiceFetch().fetch_invoice()
        q.put([data_claimNos, data_invoices, supplierName, claims_rule])
        pass
    pass


def start_browser(port):
    # 执行命令
    os.system(f'chrome.exe --remote-debugging-port={port} --user-data-dir="D:\AutomationProfile{port}"')
    pass


def start_consumer(login_url='', username='', password='', port=0):
    LoginSelenium(login_url=login_url, username=username, password=password, port=port)


threading.Thread(target=producer, daemon=False, name='线程保携金融平台').start()   # 启动一次即可

threading.Thread(target=start_browser, args=(9522,), daemon=False, name='9522线程Chrome浏览器').start()
time.sleep(1)
threading.Thread(target=start_consumer, args=("http://9.0.9.11/workbench/workbench/login.html", "15168204207", "990214Lys", 9522), daemon=False, name='9522').start()
time.sleep(5)

threading.Thread(target=start_browser, args=(9524,), daemon=False, name='9524线程Chrome浏览器').start()
time.sleep(1)
threading.Thread(target=start_consumer, args=("http://9.0.9.11/workbench/workbench/login.html", "15168204207", "990214Lys", 9524), daemon=False, name='9524').start()
time.sleep(5)

threading.Thread(target=start_browser, args=(9525,), daemon=False, name='9525线程Chrome浏览器').start()
time.sleep(1)
threading.Thread(target=start_consumer, args=("http://9.0.9.11/workbench/workbench/login.html", "15168204207", "990214Lys", 9525), daemon=False, name='9525').start()


q.join()    # 等待所有子线程结束

print('主线程结束')

