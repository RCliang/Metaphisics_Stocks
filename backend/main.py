from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, FastAPI
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
import uvicorn
from crud import *
from models import *
import os
import sys
import futu as ft
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
# from passlib.context import CryptContext
# from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
from futu_api import *
from futu import SubType, KLType, RET_OK, AuType
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from utils import read_yaml
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)

config = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... startup code ...
    global config
    config = read_yaml(os.path.join(ROOT_PATH, "backend/config.yaml"))  # 从yaml文件读取配置
    print("配置加载完成：", config)
    yield

origins = ["*"]
app = FastAPI(
    title="Futu project",
    description="Futu project 项目文档：",
    version="1.0.0",
    docs_url="/api/docs",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)
app.mount('/static', app=StaticFiles(directory=os.path.join(ROOT_PATH,'backend/static')), name='static')

# SECRET_KEY = "86a39e19831f33b7c8e8757d2e77a6e71b2fbbd117690e3b88f323b8bd5e2e95"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_schema = OAuth2PasswordBearer(tokenUrl="/jwt/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 根据股票名称获取股票代码
@app.get("/api/query_stock_plate")
async def query_stock_plate(stock_name: str, db: Session = Depends(get_db)):
    stock_code = get_stock_code(db, stock_name)
    if stock_code:
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = quote_ctx.get_owner_plate([stock_code])
        if ret == ft.RET_OK:
            plate_name = data['plate_name'].values.tolist()
            plate_names = ','.join(plate_name)
        quote_ctx.close()
        return {"stock_code": stock_code, "plate_name": plate_names}
    else:
        return {"error": "stock not found", "code": 404}

@app.get("/api/query_stock_basic_info")
async def query_stock_basic_info(stock_name: str, db: Session = Depends(get_db)):
    stock_code = get_stock_code(db, stock_name)
    cols_dict = config['need_cols']
    print(stock_code)
    if stock_code:
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = quote_ctx.get_market_snapshot([stock_code])
        print(data)
        if ret == ft.RET_OK:
            data = data.loc[:, list(cols_dict.keys())]
            if data['plate_valid'].values[0] == False:
                data = data.drop(['plate_valid', 'plate_raise_count', 'plate_fall_count'], axis=1)
            res = ''
            for col in data.columns:
                res += cols_dict[col] + ':' + str(data[col].values[0]) + ','
            quote_ctx.close()
            return {"stock_code": stock_code, "basic_info": res, "code": 200}
        else:
            quote_ctx.close()
            return {'stock_code':'stock not found', 'basic_info': 'None', "code": ret}
    else:
        return {'stock_code':'stock not found', 'basic_info': 'None', "code": 404}
    
@app.get("/api/query_stock_data")
async def query_stock_data(stock_code: str, db: Session = Depends(get_db)):
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_sub, err_message = quote_ctx.subscribe([stock_code], [SubType.K_DAY], subscribe_push=False)
    if ret_sub == RET_OK:
        ret, data = quote_ctx.get_cur_kline(stock_code, 2, KLType.K_DAY, AuType.QFQ)
        if ret == RET_OK:
            need_cols = ['time_key', 'open', 'close', 'high', 'low', 'volume']
            res = {}
            for item in need_cols:
                res[item] = data[item].values.tolist()
            return {'code':200, 'data':res}
        else:
            return {'code':404, 'data':'stock not found'}
    else:
        return {'data': err_message, 'code': 500}

    
if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True, workers=1)
