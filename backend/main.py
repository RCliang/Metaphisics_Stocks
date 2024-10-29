from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, FastAPI
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
import uvicorn
from crud import *
from models import *
import hashlib
import futu as ft
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
from futu_api import *
from fastapi.middleware.cors import CORSMiddleware


origins = ["*"]
app = FastAPI(
    title="Futu project",
    description="Futu project 项目文档：",
    version="1.0.0",
    docs_url="/docs"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)
app.mount('/static', app=StaticFiles(directory='./backend/static'), name='static')

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
@app.get("/query_stock_plate")
async def query_stock_plate(stock_name: str, db: Session = Depends(get_db)):
    stock_code = get_stock_code(db, stock_name)
    print(stock_code)
    if stock_code:
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret, data = quote_ctx.get_owner_plate([stock_code])
        print(data)
        if ret == ft.RET_OK:
            plate_name = data['plate_name'].values.tolist()
            plate_names = ','.join(plate_name)
        quote_ctx.close()
        return {"stock_code": stock_code, "plate_name": plate_names}
    else:
        return {"error": "stock not found", "code": 404}



if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True, workers=1)
