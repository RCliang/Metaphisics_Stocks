import os
import pandas as pd
import time
import hashlib
import base64
import hmac
import json
import requests
from futu import *
from matplotlib import pyplot as plt
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