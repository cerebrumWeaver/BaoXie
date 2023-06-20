import requests
from requests import utils
import json

from DynamicCode import dynamicCode

base_url = 'http://47.103.80.27:8850'  # 本地测试地址
static_url = base_url + '/static'
target_url = "https://ins.chinalife-p.com.cn//workbench/workbench/login.html"
target_url = "http://9.0.9.11/workbench/workbench/login.html"
# 机器人名称
bot_name = "中华联机器人"
# 机器人连接密钥
secret = ""
# 终端名称
partnerName = ''
username = "220183198910225617"
password = "Ljy@123456"
c_id = 'ZHL_XJ'

auth_code = dynamicCode().getDynamicCode(username)

url_login = 'http://9.0.9.11/workbench/controller/workbench/login/login?redUrl='
headers_login = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36', }
json_login = {
    "userName": "s9jrJ0tJ+rkeDEdmdXqZTGZnuF/Ecu5ht7unz/buTNSQz08CiEBkGjBRRNVm+6QbhEUbLl+KS7cEseF6t/MqjRJ/uILsLJ3fYVf6ha/ALxaWkI9ZXyAK28f76fHZWceSaIyD4awHno5x9KxwXhgh0X5rbyMC8LbI2r8oR//tXeehel59Sy+Hf1FDEEiXsKsmI5XjfGjkcgoEmkr4UPS2ZEq6nF1h4hCewLNAvRD2AwKL74tLuOkPxUDw0914FyXPkeFtVzlePys9N7OLqGOwD9TZMDfZgjCD6Dm9qtZojlwKIc8a0uZRvkafp52de7RKqlnhop5GeVK8KVYIGe0xeg==",
    "userPwd": "7oERFNgb5qgW4qIoDT9vzpvRgEQ375tnbS2P62J+lKLLvnZ+3ETD3ibtds0okJMZNEV8HZGtq09pSAkCicP2ISHE72xuExXHAyLdsXrqIH95St+U4sp9neu3HrHDSTK6U6bPYF6lJiAyG2Kgbssy1d25KGNTy0dXWkXb4X9gIfL5FyVJP1jrQQfb+P1ejHhCNU4fZVhhv63lU7aLrGi7uBYV3czR4kwBP/NejIHCAUdwyBaoTbibjbNaAxKi7Yv9wvkLltPEMVxFHvzPD58G1Hie0SWa2uO0F7UlNvIh9zg9bOvPFA98gk2NJ2m4HRkBaJRj8VHp5jEhJKXG+06BrQ==",
    "weiXinCode": "964572",
    "loginStatus": None
}
json_login = {
    "userName": "wtvk8ndWwKIMWRflxl3PjGihLTYEPEqcZRmXYl7gpnpvozfn8NPc/fVCO5V4xS5llrWQqxHq8aI56z7Ljc8xjeoILgfzLlqhID78eJQJ6Cb+Myu7ttCg07RT78PObjJMNwkP6mDtVgfIX6Ffgmvo8uQ7ZxfgRxrfu1u67e4MRrmDoMWG41HpYZRARYdphoAbPbLus50dPi6DuFW0W9s078O+MkPdfi5C4z6NWOK8ZbbwIN5DsFeYGCCTKYB/attNK6VILnZ9ty8Tgm+5nFC+Awc4N0gtIvWHUoWPYw2TdHlw7IQ8lusUoRjIKXQ3n8gD0LYsYHsYKtBIrHdM2BII6A==",
    "userPwd": "vEyfzPVSTRU7hXjKyNyZhiHSYDQOO1neAncIlfwDoKEeovcn6p/zMX4ZDbM1x6FsjzMT9aMACVt+ZdvDLyqAmv/tVUyTzDnAWziz8VG0NguLL7t+7ZyMxmvV7yVlGvKP5U5ytoXy5H/pz1EsIClEeUkjy1Hg4tRTQiJHv9cZje6rAvCcwMnnMxsIMsjKPG7FBkJ3+4Zh72KgfkB5r22ZUP2mkgtCCiyxYg9M2KUReXwGdzVBjzsmHQ8URpCnPEh47wOCwqfMAzxDS+oOfnhyY2zBydKseuw/7WeABemzUQXPBKzveD0cLzZgKv/PMeFI18X2AQ4iMfvjV09qoJ0jsA==",
    "weiXinCode": f"{auth_code}",
    "loginStatus": None
}
json_login = {
    "userName": "5S8kpDr4/FzmgM2G+OPVmp/5AztWYWSPQCdbXn7id8pertMo/TARb9TQoGlkmnKyMm2xam90dE9I9LjF4E4LIMv5L/KzwDhE2BlsHV7j/4kjMfoyJwZYK0l49HG6l1/uUA1pZMzQmMhiDwGzL2AyL8vq6RoFNypqn6uGwQbajOO3eXJ9dcTpCYNlkoenL0bMwWVtmZCP4VeUfF+MJU7yTpmMQtzuko6tKc+p5/EFfEsbPsIear4ECwWh9A3KsWzfJAcW7+JahDQsM1Yu1PvgozuC2Oe7VUUbJ7ttiAeZWjPhqayJv1Osns2jH+OPO+RYj1Yigb5r04nDq+mRBOSdTQ==",
    "userPwd": "ZBMvXgW/79JUqlREHiOvThiC+X0Sd6rplbvDLjWWODndp5NCYG74gA4DPrk+oD7oSa070Y52ASg3/4Z9ORLQPxlxoSU06gYRiqI7gyVL3k9P/vsOFefmbS9vW6ESA/O9MnT3qr6jR1Gghol0/7JkgyvtYfv2AnTZmj7aF82tsBX6slT2DtzRIsqqIm1J1KPCqoZoXYhtGeiPDB6wJOhfddze4bsFGRCxKUgIJ59pzNYWVv9LKX2Q91oDaB8fX39gEST28bXokMPuY4Mztp2z6cgqAwIN1k9Vrakkg/w4fJQNZF9rhBEbVKeDZ8KQvBV3jRoEu9K6lng7f96lKiMm2g==",
    "weiXinCode": f"{auth_code}",
    "loginStatus": None
}

url_pending_invoice01 = 'http://9.0.9.11/workbench/controller/workbench/jurisdictionmenu/findLiPeiUrlByName?name=%E5%BE%85%E5%BC%80%E5%8F%91%E7%A5%A8%E6%89%93%E5%8C%85&url=/newclaimcar/car/template/prplinvoiceready/prplinvoicereadybatch/UIPrpLInvoiceReadyQuery.html'

url_pending_invoice02 = 'http://9.0.9.11/newclaimcar/controller/claim/prplblacklistauditask/prplblacklistauditask/initComNameSelect'
headers_pending_invoice = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
}

url_pending_invoice03 = 'http://9.0.9.11/newclaimcar/controller/claim/prpllog/prpDCompany/findByProvinceComCodeTwo?strComcode=22010035'

import requests.utils
import json


def save_cookies(_data):
    """" 保存cookies成文件
    files_path： 文件保存路径
    _data: 需要保存的参数
    """
    '_pk_id.18.92e3=1bbfe1997afc172f.1680774166.; _pk_ses.18.92e3=1;'
    cookies_dict = utils.dict_from_cookiejar(_data)
    print(f'保存：{cookies_dict}')
    cookies_dict['_pk_id.18.92e3'] = '1bbfe1997afc172f.1680774166.'
    cookies_dict['_pk_ses.18.92e3'] = '1'
    return utils.cookiejar_from_dict(cookies_dict)


def login_():
    # rep = requests.post(url_login, headers=headers_login, json=json_login)
    session_ = requests.Session()
    print(f'登陆前cookie：{session_.cookies.copy()}')
    rep = session_.post(url_login, headers=headers_login, json=json_login)
    print(f'登陆后cookie：{session_.cookies.copy()}')
    cookie = save_cookies(session_.cookies.copy())
    session_.cookies = cookie
    print(rep.json())

    # pending_invoice01 = session_.post(url=url_pending_invoice01, headers=headers_pending_invoice)
    # print(f'待打包01后cookie：{session_.cookies.copy()}')
    # print(pending_invoice01.text)

    # pending_invoice02 = session_.post(url=url_pending_invoice02, headers=headers_pending_invoice)
    # print(f'待打包02后cookie：{session_.cookies.copy()}')
    # print(pending_invoice02.json())

    # session_ = requests.Session()
    # session_.get(url_pending_invoice03, headers=headers_login)
    print(f'新值：{session_.cookies}')
    return session_


login_()

# login_()
# print(auth_code)
# login_()
# 请求验证码
# def get_login_code():
#     # 发送请求协助
#     # url = self.base_url + "/api/rpa/captcha_request"
#     url = base_url + "/api/rpa/captcha_request"
#     params = {
#         # "clientOrgNo": self.cid,
#         "clientOrgNo": c_id,
#         # "unikey": f"{self.u}",
#         "unikey": f"{username}",
#         "timeout": 3590
#     }
#     params1 = {
#         # "unikey": f"{self.u}",
#         "unikey": f"{username}",
#         "timeout": 3590
#     }
#     # resp = requests.post(url, params=params, files=None, headers=self.headers, verify=False)
#     resp = requests.post(url, params=params, files=None, verify=False)
#     resp.raise_for_status()
#     # 获取接收到的验证码
#     # url1 = self.base_url + "/api/rpa/captcha_code"
#     url1 = base_url + "/api/rpa/captcha_code"
#     code_data = None
#     while True:
#         # resp = requests.get(url1, params=params1, headers=self.headers, verify=False)
#         resp = requests.get(url1, params=params1, verify=False)
#         resp.raise_for_status()
#         # 获取验证码
#         code = resp.json()
#         if code and code.__contains__("data"):
#             code_data = code["data"]
#         if code_data:
#             print(code_data)
#             return code_data
#         else:
#             print('为空')
#             self.wait(5)


# get_login_code()
