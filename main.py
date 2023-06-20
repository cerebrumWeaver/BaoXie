import sys
import time
import logging

from webdriver_manager.chrome import ChromeDriverManager  # 三方库安装驱动

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

chromeOptions = ChromeOptions()

# chromeOptions.add_argument('--start-maximized')  # 最大化窗口
chromeOptions.binary_location = "D:/chrome83/ChromePortable/App/Google Chrome/chrome.exe"
# chromeOptions.add_experimental_option('detach', True)  # 保持浏览器打开状态
# chromeOptions.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chromeOptions, service=ChromeService(ChromeDriverManager().install()))
driver.implicitly_wait(10)  # 隐式等待
driver.get('https://icar.epicc.com.cn/zncd/#/picc/index')


# # 模拟登录
# driver.find_element(by=By.XPATH, value='//*[@id="app-scroll"]/div/form/div[2]/div[1]/div/div/div/input').click()    # 展开选择框
#
# driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[1]/div[1]/ul/li[2]').click()  # 选择 上海
#
# driver.find_element(by=By.XPATH, value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/div[1]/div/div[1]/input').send_keys('A310106075')  # 输入用户名
#
# driver.find_element(by=By.XPATH, value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/div[2]/div/div/input').send_keys('Baoxie03')  # 输入密码
#
# driver.find_element(by=By.XPATH, value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/div[3]/div/div/input').send_keys('256833')  # 输入密码
#
# driver.find_element(by=By.XPATH, value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/button').click()  # 点击登录


def login_ok(driver_):
    # 模拟登录
    driver_.find_element(by=By.XPATH,
                         value='//*[@id="app-scroll"]/div/form/div[2]/div[1]/div/div/div/input').click()  # 展开选择框

    driver_.find_element(by=By.XPATH, value='/html/body/div[2]/div[1]/div[1]/ul/li[2]').click()  # 选择 上海

    driver_.find_element(by=By.XPATH,
                         value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/div[1]/div/div[1]/input').send_keys(
        'A310106075')  # 输入用户名

    driver_.find_element(by=By.XPATH,
                         value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/div[2]/div/div/input').send_keys(
        'Baoxie03')  # 输入密码

    driver_.find_element(by=By.XPATH,
                         value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/div[3]/div/div/input').send_keys(
        264166)  # 输入安全令

    driver_.find_element(by=By.XPATH, value='//*[@id="app-scroll"]/div/form/div[2]/div[2]/button').click()  # 点击登录

    # login_info = driver.find_element(by=By.XPATH,
    #                                  value='/html/body/div[3]/div/div[2]/div[1]/div[2]/p').text
    print(f'函数内部申明driver：{id(driver_)}')
    return driver_


def log():
    format = "%(asctime)s - %(levelname)s - %(message)s"  # 美式
    dateformat = "%m/%d/%Y %H:%M:%S %p"  # 中式

    # 文件句柄
    file_handler = logging.FileHandler('登录刷新日志.log', encoding='utf-8')

    # 流句柄
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        # filename='日志.log', # 设置文件句柄后注释
        format=format,
        datefmt=dateformat,
        handlers=[
            file_handler,
            # stream_handler,
        ]
    )


log()
wb = login_ok(driver)
time.sleep(500)
print(f'函数返回driver：{id(wb)}')

refresh_counts = 0
# while True:
#     time.sleep(480)
#     driver.refresh()
#     refresh_counts += 1
#     logging.info(f'info：页面已刷新{refresh_counts}次')



# login_success_or_failure, driver = login_ok(driver)  # 启动登录
# driver.find_element(by=By.XPATH, value='/html/body/div[3]/div/div[3]/button').click()
#
# print(login_success_or_failure)
# try:
#     assert login_success_or_failure != '人保安全令校验失败 ！'
# except Exception as e:
#     logging.critical(e)
#     logging.info(login_success_or_failure)
# else:
#     refresh_counts = 0
#     while True:
#         time.sleep(500)
#         driver.refresh()
#         refresh_counts += 1
#         logging.info(f'info：页面已刷新{refresh_counts}次')
# finally:
#     pass
