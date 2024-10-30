import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
import pandas as pd
import numpy as np
from backend.utils import FeishuApp
from futu import *
from matplotlib import pyplot as plt
from dotenv import load_dotenv

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

def draw_kdj(res:pd.DataFrame, code:str):
    plt.figure(figsize=(10,5))
    plt.plot(res['k'], marker='x', markersize=3, color='red')
    plt.plot(res['d'], marker='o', markersize=3, color='green')
    plt.plot(res['j'], marker='o', markersize=3, color='black')
    plt.legend(['k', 'd', 'j'])
    plt.savefig(os.path.join(ROOT_PATH, f'sechdule_task/static/{code}_kdj.png'))
    # plt.show()
    return
def get_kdj_data(data:pd.DataFrame):
    k, d, j = calculate_kdj(data['high'], data['low'], data['close'])
    res = pd.DataFrame({'k': k, 'j': j, 'd': d, 'close': data['close']})
    res = res.dropna()
    return res
def j_strategy_short(res:pd.DataFrame):
    res['j_diff'] = res['j'].diff()
    res['j_diff'] = res['j_diff'].apply(lambda x: 1 if x < 0 else 0)
    res['close_diff'] = res['close'].diff()
    res['close_diff'] = res['close_diff'].apply(lambda x: 1 if x > 0 else -1)
    if sum(res['j_diff'].to_list()[-5:]) >= 3 and res['j'].to_list()[-1] < 0:
        print("long point!")
        return True
    else:
        return False

def main():
    load_dotenv()
    target_code = {'SH.688385': '复旦微电',
                    'SH.688318': '财富趋势',
                    'SH.688041': '海光信息'}
    receive_id = 'ou_5117ddde720ef1b546f1ceacab6a945b'
    app_id = os.environ.get("APP_ID")
    app_secret = os.environ.get("APP_SECRET")
    feishu_app = FeishuApp(app_id, app_secret)
    data_list = get_latest_data(list(target_code.keys()), ['high', 'low', 'close'], 30, k_type=KLType.K_DAY, sub_type=SubType.K_DAY)
    for code, data in data_list.items():
        res = get_kdj_data(data)
        draw_kdj(res, code)
        response = feishu_app.upload_image(os.path.join(ROOT_PATH, f'sechdule_task/static/{code}_kdj.png'))
        if response['code'] != 0:
            print(response)
            feishu_app.access_token = feishu_app.get_access_token()
            response = feishu_app.upload_image(os.path.join(ROOT_PATH, f'sechdule_task/static/{code}_kdj.png'))
        pic_id = response['data']['image_key']
        title = "关注提醒！！"
        if j_strategy_short(res):
            content = f"{target_code[code]} 短期J线已到20以下，请关注!"
        else:
            content = f"{target_code[code]} 短期J线未到20以下，无需关注!"
        feishu_app.send_message_card(feishu_app.create_msg_card(receive_id=receive_id, title=title, content=content, pic_id=pic_id))
            

if __name__ == "__main__":
    main()