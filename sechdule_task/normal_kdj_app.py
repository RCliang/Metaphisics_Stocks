import os
import sys
from dotenv import load_dotenv
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
import pandas as pd
import numpy as np
from backend.utils import FeishuApp, calculate_kdj, get_latest_data, get_selected_stock
from futu import *
from matplotlib import pyplot as plt

def draw_kdj(res:pd.DataFrame, code:str):
    plt.figure(figsize=(10,5))
    plt.plot(res['k'], marker='x', markersize=3, color='red')
    plt.plot(res['d'], marker='o', markersize=3, color='green')
    plt.plot(res['j'], marker='o', markersize=3, color='black')
    plt.legend(['k', 'd', 'j'])
    plt.savefig(os.path.join(ROOT_PATH, f'sechdule_task/static/norm_{code}_kdj.png'))
    # plt.show()
    return
def get_kdj_data(data:pd.DataFrame):
    k, d, j = calculate_kdj(data['high'], data['low'], data['close'])
    res = pd.DataFrame({'k': k, 'j': j, 'd': d, 'close': data['close']})
    res = res.dropna()
    return res
def j_strategy_short(res:pd.DataFrame, threshold:int):
    res['j_diff'] = res['j'].diff()
    res['j_diff'] = res['j_diff'].apply(lambda x: 1 if x < 0 else 0)
    res['close_diff'] = res['close'].diff()
    res['close_diff'] = res['close_diff'].apply(lambda x: 1 if x > 0 else -1)
    if sum(res['j_diff'].to_list()[-5:]) >= 3 and res['j'].to_list()[-1] < threshold:
        print("long point!")
        return True
    else:
        return False
    
def main():
    load_dotenv()
    receive_id = 'ou_5117ddde720ef1b546f1ceacab6a945b'
    app_id = os.environ.get("APP_ID")
    app_secret = os.environ.get("APP_SECRET")
    target_code = get_selected_stock()
    feishu_app = FeishuApp(app_id, app_secret)
    data_list = get_latest_data(list(target_code.keys()), ['high', 'low', 'close'], 30, k_type=KLType.K_DAY, sub_type=SubType.K_DAY)
    for code, data in data_list.items():
        res = get_kdj_data(data)
        if j_strategy_short(res, 0):
            content = f"{target_code[code]} 短期J线已到20以下，请关注!"
            draw_kdj(res, code)
            response = feishu_app.upload_image(os.path.join(ROOT_PATH, f'sechdule_task/static/norm_{code}_kdj.png'))
            if response['code'] != 0:
                print(response)
                feishu_app.access_token = feishu_app.get_access_token()
                response = feishu_app.upload_image(os.path.join(ROOT_PATH, f'sechdule_task/static/norm_{code}_kdj.png'))
            pic_id = response['data']['image_key']
            title = "买入关注提醒！！"
            feishu_app.send_message_card(feishu_app.create_msg_card(receive_id=receive_id, title=title, content=content, pic_id=pic_id))
            

if __name__ == "__main__":
    main()