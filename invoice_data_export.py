import pandas as pd
import requests
import time
from datetime import datetime, timedelta


import time

import requests
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

import logging as log_
from utils.log import Log
import copy
import pandas as pd
from loguru import logger
from pending_invoice_fetch import PendingInvoiceFetch


class LoginSelenium:
    def __init__(self, login_url='', username='', password=''):
        Log()  # 初始化日志配置
        self.login_url = login_url
        self.username = username
        self.password = password

        self.chromeOptions = ChromeOptions()
        self.chromeOptions.add_experimental_option("debuggerAddress", "127.0.0.1:9523")
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
        pass

    def login_page(self):
        self.driver.get(self.login_url)
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div/span').click()
        self.driver.find_element(by=By.XPATH, value='//*[@id="userName"]').send_keys(self.username)
        self.driver.find_element(by=By.XPATH, value='//*[@id="userPwd"]').send_keys(self.password)
        self.driver.find_elements(by=By.XPATH, value='//*[@id="weiXinCode"]')[0].send_keys(dynamicCode().getDynamicCode('330102199902143023'))
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[2]/c-button[1]/span').click()

        try:
            self.driver.find_element(by=By.XPATH, value='/html/body/div[4]/div/div[3]/div[2]').click()
        except Exception as e:
            log_.info("未显示弹窗：’您已在其他地方登录，是否强制登录？‘")
        time.sleep(3)
        self.driver.find_element(by=By.XPATH, value='//*[@id="selectStructure"]/i[1]').click()

        print(self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[1]').text)
        if self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[1]').text == '杭州理赔/客服分中心':
            self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[1]').click()
        else:
            self.driver.find_element(by=By.XPATH, value='/html/body/div[5]/div/c-listview/ul/li[2]').click()
        self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[3]/c-button').click()  # 点击确定按钮取消弹窗
        time.sleep(5)
        log_.info('登录成功！！！')
        self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="contentIframe"]/iframe'))     # 定位 主页 iframe
        self.driver.find_element(by=By.XPATH, value='//*[@id="carousel1"]/div[2]/div[1]/li[9]').click()  # 点击 待开发票打包

        self.driver.switch_to.default_content()  # 重置iframe
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[2]/img[2]').click()  # 点击符号：>
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[1]/ul/li[9]/span').click()  # 点击 待开发票打包
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div[1]/span').click()  # 回到符号：>页面
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[2]/img[2]').click()  # 点击符号：>
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/div[2]/div[1]/ul/li[14]/span').click()  # 点击 导出文件查询
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div[2]/i').click()  # 关闭符号：>页面
        return self.driver
        pass

    def query_pending_invoice_packing(self, start, end):
        self.driver.switch_to.default_content()  # 重置iframe
        self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/nav/tabs/tab[2]/div[1]/span').click()  # 点击 待开发票打包tab

        self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[2]/c-iframe/iframe'))  # 定位 待开发票打包 iframe
        start_time_element = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[4]/field[2]/h-box/flex-box[1]/c-datepicker/input')
        while start_time_element.get_attribute('value') != start:
            start_time_element.clear()  # 起始时间
            time.sleep(1)
            start_time_element.send_keys(start)

        end_time_element = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[4]/field[2]/h-box/flex-box[2]/c-datepicker/input')  # 结束时间
        while end_time_element.get_attribute('value') != end:
            end_time_element.clear()  # 结束时间
            time.sleep(1)
            end_time_element.send_keys(end)
        print('休眠5秒钟再查询')
        time.sleep(5)
        self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[9]/c-button[1]').click()  # 查询按钮

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

    def export_and_query(self, start, end):
        export_code = ''
        while True:
            try:
                print('try语句')
                # 导出按钮 点击
                export_xpath = '/html/body/div[1]/div[2]/div/div[2]/div/c-button[1]/span'
                export_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', export_xpath)))
                export_element.click()

                sys_info_xpath = '//*[@id="c-notify-tip-container"]/message/p'
                sys_info_element = WebDriverWait(self.driver, 10, 0.2).until(EC.presence_of_element_located(('xpath', sys_info_xpath)))
                while not sys_info_element.text:
                    pass
                if sys_info_element.text == '请先进行查询操作！':
                    print('请等待查询完毕！休眠120秒钟')
                    time.sleep(120)
                    continue
                    pass
                # else:
                #     error_xpath = '/html/body/div[5]/div/div[3]/div[3]/span'
                #     error_element = self.driver.find_element(by='xpath', value=error_xpath)
                #     error_element.click()
                #     print('查询列表失败，请稍后再试，或联系系统管理员！休眠10秒钟')
                #     time.sleep(10)
                #     continue

                pass
            except Exception as e:
                try:
                    # 导出成功 弹窗
                    export_success_xpath = '/html/body/div[5]/div/div[2]/div[2]'
                    export_success_element = WebDriverWait(self.driver, 10, 0.2).until(EC.presence_of_element_located(('xpath', export_success_xpath)))
                    while not export_success_element.text:
                        pass
                except Exception as e:
                    print('导出成功弹窗元素定位失败，休眠5秒钟')
                    time.sleep(5)
                    continue
                else:
                    if '导出成功' in export_success_element.text:
                        export_code = export_success_element.text.split('：')[-1]
                        print(export_code)
                        # 关闭导出成功 弹窗
                        close_export_success_xpath = '/html/body/div[5]/div/div[3]/div[3]/span'
                        close_export_success_element = WebDriverWait(self.driver, 10, 0.5).until(EC.presence_of_element_located(('xpath', close_export_success_xpath)))
                        close_export_success_element.click()
                        break
                        pass

                pass
        if export_code:
            while True:
                try:
                    self.driver.switch_to.default_content()  # 重置 导出文件tab iframe
                    # 定位 导出文件查询tab
                    export_file_download_xpath = '//*[@id="tabControl"]/nav/tabs/tab[3]/div[1]/span'
                    export_file_download_element = self.driver.find_element(by='xpath', value=export_file_download_xpath)
                    export_file_download_element.click()

                    self.driver.switch_to.default_content()  # 重置 导出文件tab iframe
                    '//*[@id="tabControl"]/contents/content[3]/c-iframe/iframe'
                    self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='//*[@id="tabControl"]/contents/content[3]/c-iframe/iframe'))  # 定位 导出文件tab iframe
                    # self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='/html/body/v-box/flex-box/c-iframe'))  # 再定位 导出文件tab iframe
                    self.driver.switch_to.frame(self.driver.find_element(by=By.XPATH, value='/html/body/v-box/flex-box/c-iframe/iframe'))  # 再定位 导出文件tab iframe
                    export_code_xpath = '/html/body/div/div[2]/div/div[1]/c-query-form/fields[1]/field[2]/c-input/input'
                    export_code_element = self.driver.find_element(by='xpath', value=export_code_xpath)
                    while export_code_element.get_attribute('value') != export_code:
                        export_code_element.clear()
                        print('send_keys方法输入错误的导出码，休眠0.5秒钟，首次出现该错误请忽略')
                        time.sleep(0.5)
                        export_code_element.send_keys(export_code)

                    # 点击查询
                    export_code_query_xpath = '/html/body/div[1]/div[2]/div/div[1]/c-query-form/fields[2]/c-button[1]/span'
                    export_code_element = self.driver.find_element(by='xpath', value=export_code_query_xpath)
                    export_code_element.click()

                    # # 关闭导出查询 弹窗
                    # close_export_code_window_xpath = '/html/body/div[2]/div/div[3]/div[3]/span'
                    # close_export_code_window_element = self.driver.find_element(by='xpath', value=close_export_code_window_xpath)
                    # close_export_code_window_element.click()
                    # print(f'导出码{export_code}后台查询为空，休息5秒后再查询')
                    # time.sleep(5)

                    # 关闭 未查询到符合条件的文件,请重新录入查询条件! 弹窗
                    close_export_code_window_xpath = '/html/body/div[2]/div/div[3]/div[3]/span'
                    close_export_code_window_element = WebDriverWait(self.driver, 10, 0.2).until(EC.presence_of_element_located(('xpath', close_export_code_window_xpath)))
                    close_export_code_window_element.click()
                    print(f'导出码{export_code}后台查询为空，休息20秒后再查询')
                    time.sleep(20)
                    pass
                except Exception as e:
                    try:
                        download_xpath = '/html/body/div[1]/div[2]/div/div[2]/c-table/div[1]/div[2]/ul/div/cell[9]/div/div/a[1]'
                        download_element = self.driver.find_element(by='xpath', value=download_xpath)
                        download_element.click()
                        print('正在下载文件，休眠5秒钟，等待下载完')
                        time.sleep(5)
                        pass
                    except Exception as e:
                        print('下载失败，30秒钟后再下载')
                        time.sleep(30)
                        try:
                            # 再次关闭 未查询到符合条件的文件,请重新录入查询条件! 弹窗
                            close_export_code_window_xpath = '/html/body/div[2]/div/div[3]/div[3]/span'
                            close_export_code_window_element = WebDriverWait(self.driver, 10, 0.2).until(EC.presence_of_element_located(('xpath', close_export_code_window_xpath)))
                            close_export_code_window_element.click()
                            pass
                        except Exception as e:
                            pass
                        continue
                        pass
                    else:
                        self.driver.switch_to.default_content()     # 重置iframe
                        print('下载成功')
                        print(f'[{start},{end}]下载成功')
                        break


# 从客户系统爬数据
def query_invoice_ready(start, end):
    url_ = 'http://9.0.9.11/newclaimcar/controller/claim/prplinvoiceready/prplInvoiceReady/queryInvoiceReady'
    params_ = {'from': 0, 'limit': 50}
    headers_ = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    }
    json_ = {
          "payConfirmEndTime": f"{end}T00:00:00.000+0800",
          "payConfirmStartTime": f"{start}T00:00:00.000+0800",
          "batchEndTime": "",
          "batchStartTime": "",
          "state": "0",
          "certainDeptCode": "",
          "comCode": "33010000",
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
            for i in range(0, entity_count, 50):
                params_inner = {'from': i, 'limit': 50}
                rep_inner_json = session_.post(url=url_, headers=headers_, params=params_inner, json=json_).json()
                datasets += rep_inner_json.get('data$')
    except Exception as e:
        time.sleep(2)
        return query_invoice_ready(start, end)
    else:
        object_ids_ = {}
        for dataset in datasets:
            object_id = dataset.get('objectId')  # id号
            loss_name = dataset.get('lossName')  # 损失标的（即车牌号）
            object_ids_[str(object_id)] = loss_name
        return datasets, session_, object_ids_
    finally:
        pass


def get_timedelta():
    current_date = datetime.now()
    current_date = datetime.strptime('2023-06-13', '%Y-%m-%d')
    current_date = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
    json_list = []
    for _ in range(10):
        end_time = pd.Timestamp(current_date).strftime('%Y-%m-%d')
        start_time = pd.Timestamp(datetime.strptime(end_time, '%Y-%m-%d') - timedelta(days=89)).strftime('%Y-%m-%d')
        current_date = pd.Timestamp(start_time) - timedelta(days=1)
        # json_ = {
        #     "payConfirmEndTime": f"{end_time}T23:59:59.000+0800",
        #     "payConfirmStartTime": f"{start_time}T23:59:59.000+0800",
        #     "batchEndTime": "",
        #     "batchStartTime": "",
        #     "state": "0",
        #     "certainDeptCode": "",
        #     "comCode": "33010000",
        #     "accountName": '',
        #     "taskFlag": "all",
        #     "includeDSFlag": False,
        #     "includeCBFlag": True,
        #     "tpFlag": False,
        #     "inLikeFlag": False
        # }
        # params = {
        #     "payConfirmEndTime": f"{end_time}T23:59:59.000 0800",
        #     "payConfirmStartTime": f"{start_time}T23:59:59.001 0800",
        #     "batchEndTime": "",
        #     "batchStartTime": "",
        #     "state": "0",
        #     "certainDeptCode": "",
        #     "comCode": "33010000",
        #     "taskFlag": "all",
        #     "includeDSFlag": False,
        #     "includeCBFlag": True,
        #     "tpFlag": False,
        #     "inLikeFlag": False
        # }
        json_list.append((start_time, end_time))
    return json_list


if __name__ == '__main__':
    timedelta_query = get_timedelta()
    print(timedelta_query[:1])
    # datasets = query_invoice_ready('2023-06-12', '2023-06-12')[0]
    # print(datasets)
    # driver = LoginSelenium(login_url = "http://9.0.9.11/workbench/workbench/login.html", username = "220183198910225617", password = "Ljy@123456").login_page()
    login_obj = LoginSelenium(login_url="http://9.0.9.11/workbench/workbench/login.html", username="15168204207", password="990214Lys")
    driver_login = login_obj.login_page()
    # for s, e in [('2023-06-12', '2023-06-12'), ('2023-06-13', '2023-06-13')]:
    for s, e in timedelta_query:
        login_obj.query_pending_invoice_packing(s, e)
    # driver_query_pending_invoice_packing = login_obj.query_pending_invoice_packing('2023-06-12', '2023-06-12')

        # cookie_query, cookie_jar_query = login_obj.query_pending_invoice_packing_cookies()

        login_obj.export_and_query(s, e)  # 打开 任务处理tab

