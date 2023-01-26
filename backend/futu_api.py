from futu import OpenQuoteContext, PeriodType, ModifyUserSecurityOp, KLType, Market, SecurityType, Plate
from futu import SimpleFilter, CustomIndicatorFilter, FinancialFilter, StockField, PatternFilter, AccumulateFilter
from typing import List
import time

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)


def set_filter():
    simple_filter1 = SimpleFilter()
    simple_filter1.stock_field = StockField.MARKET_VAL
    simple_filter1.filter_min = 0
    simple_filter1.filter_max = 200
    simple_filter1.is_no_filter = True

    simple_filter2 = SimpleFilter()
    simple_filter2.stock_field = StockField.VOLUME_RATIO
    simple_filter2.filter_min = 4
    simple_filter2.filter_max = 10
    simple_filter2.is_no_filter = True

    pattern_filter = PatternFilter()
    pattern_filter.stock_field = StockField.BOLL_BREAK_UPPER
    pattern_filter.ktype = KLType.K_DAY
    pattern_filter.is_no_filter = False
    return [simple_filter1, simple_filter2, pattern_filter]


def query_result(filters: List, plate_code: str):
    nBegin = 0
    last_page = False
    ret_list = list()
    res = dict()
    while not last_page:
        nBegin += len(ret_list)
        ret, ls = quote_ctx.get_stock_filter(market=Market.SH,
                                             filter_list=filters, begin=nBegin, plate_code=plate_code)
        if ret == 0:
            last_page, all_count, ret_list = ls
            print('all count = ', all_count)
            for item in ret_list:
                res[item.stock_code] = item.stock_name
                print(item.stock_code)  # 取股票代码
                print(item.stock_name)  # 取股票名称
        else:
            print('error: ', ls)
        time.sleep(1)  # 加入时间间隔，避免触发限频
    return res
