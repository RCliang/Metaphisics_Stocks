import os
import pandas as pd
import time
import hashlib
import base64
import hmac
import json
import requests
import yaml
from futu import *
from matplotlib import pyplot as plt
import numpy as np
from requests_toolbelt.multipart.encoder import MultipartEncoder

class FeishuApp:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = self.get_access_token()
        
    def get_access_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json().get("tenant_access_token")
    
    def upload_image(self, image_path):
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        form = MultipartEncoder(
            fields={
                'image_type': 'message',
                'image': ('image.jpg', open(image_path, 'rb'), 'image/jpeg')
            }
        )
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': form.content_type
        }
        response = requests.post(url, headers=headers, data=form)
        return response.json()
    
    @staticmethod
    def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    @staticmethod
    def create_msg_card(receive_id:str, title:str, content:str, pic_id:str, template_version_name:str="1.0.1"):
        payload = {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "type": "template",
                "data": {
                    "template_id": "AAqDi1LQLLwYn",
                    "template_version_name": "1.0.1",
                    "template_variable": {
                        "title": title,
                        "content": content,
                        "pic": pic_id,
                    }
                }
            })
        }
        return payload
    def send_message_card(self, payload:dict):
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.json()
    
def calculate_kdj(high_prices, low_prices, close_prices, n=9, m1=3, m2=3):
    """
    计算KDJ指标

    参数:
    high_prices: 周期内最高价列表
    low_prices: 周期内最低价列表
    close_prices: 收盘价列表
    n: RSV的计算周期，默认9
    m1: K值的平滑周期，默认3
    m2: D值的平滑周期，默认3

    返回:
    k_list: K值列表
    d_list: D值列表
    j_list: J值列表
    """
    length = len(close_prices)
    k_list = []
    d_list = []
    j_list = []
    for i in range(length):
        if i < n - 1:
            # 在计算周期未满时，先添加None值
            k_list.append(None)
            d_list.append(None)
            j_list.append(None)
            continue
        high_max = np.max(high_prices[i - n + 1:i + 1])
        low_min = np.min(low_prices[i - n + 1:i + 1])
        rsv = ((close_prices[i] - low_min) / (high_max - low_min)) * 100
        if i == n - 1:
            k = rsv
            d = rsv
        else:
            k = ((m1 - 1) * k_list[i - 1] + rsv) / m1
            d = ((m2 - 1) * d_list[i - 1] + k) / m2
        j = 3 * k - 2 * d
        k_list.append(k)
        d_list.append(d)
        j_list.append(j)
    return k_list, d_list, j_list

def get_latest_data(codes:list, col_list:list, amount:int, k_type:KLType=KLType.K_15M, sub_type:SubType=SubType.K_15M):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_sub, err_message = quote_ctx.subscribe(codes, [sub_type], subscribe_push=False)
    if ret_sub == RET_OK:  # 订阅成功
        res_list = {}
        for code in codes:
            ret, data = quote_ctx.get_cur_kline(code, amount, k_type, AuType.QFQ) 
            if ret == RET_OK:
                res = data[col_list]
                res_list[code] = res
            else:
                print('error:', data)
    else:
        print('subscription failed', err_message)
    quote_ctx.close()
    return res_list

def get_selected_stock(group_name:str='全部'):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret, data = quote_ctx.get_user_security(group_name)
    res = {}
    if ret == RET_OK:
        if data.shape[0] > 0:  # 如果自选股列表不为空
            for i in range(data.shape[0]):  # 遍历自选股列表
                code = data['code'][i]
                name = data['name'][i]
                res[code] = name
    else:
        print('error:', data)
    quote_ctx.close()
    return res
def read_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data
    except Exception as e:
        print(f"读取YAML文件时出错: {e}")
        return None