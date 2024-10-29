from futu import OpenQuoteContext, PeriodType, ModifyUserSecurityOp, \
    KLType, Market, SecurityType, Plate
from models import StockInfo, PlateInfo
from database import SessionLocal
from typing import List
from database import Base, engine
# Base.metadata.create_all(bind=engine)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)


def flush_old_data_1(table, exchange_type: str):
    session = SessionLocal()
    session.query(table).filter(table.exchange_type == exchange_type).delete()
    session.commit()
    session.close()
    return


def flush_old_data_2(table):
    session = SessionLocal()
    session.query(table).delete()
    session.commit()
    session.close()
    return


def add_all_data(data: List):
    session = SessionLocal()
    session.add_all(data)
    session.commit()
    session.close()
    return


def transfer_data_list(df):
    all_data = []
    for item in df.values:
        all_data.append(StockInfo(stock_code=item[0],
                                  stock_name=item[1],
                                  exchange_type=item[2],
                                  delisting=item[3],
                                  listing_date=item[4]))
    return all_data


def insert_new_stock_data(market):
    ret, df = quote_ctx.get_stock_basicinfo(market, SecurityType.STOCK)
    if ret == 0:
        df = df[['code', 'name', 'exchange_type', 'delisting', 'listing_date']]
        df.columns = ['stock_code', 'stock_name', 'exchange_type', 'delisting', 'listing_date']
        df = df[df['delisting'] == False]
        data = transfer_data_list(df)
        add_all_data(data)
    else:
        raise Exception("Connection of Futu lost!")


def insert_new_plate_data(market: Market):
    all_data = []
    ret, data = quote_ctx.get_plate_list(market, Plate.CONCEPT)
    if ret == 0:
        data = data[['code', 'plate_name']]
        data.columns = ['plate_code', 'plate_name']
        temp = data.columns
        for value in data.values:
            temp_dict = {}
            for i in range(len(temp)):
                temp_dict[temp[i]] = value[i]
            all_data.append(PlateInfo(**temp_dict))
        add_all_data(all_data)
    else:
        raise Exception("Connection of Futu lost!")


def main_process():
    flush_old_data_2(PlateInfo)
    flush_old_data_2(StockInfo)
    insert_new_stock_data(Market.SH)
    insert_new_stock_data(Market.SZ)
    insert_new_plate_data(Market.SH)
    return

if __name__ == '__main__':
    main_process()