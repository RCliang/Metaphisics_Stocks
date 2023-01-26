import models
from models import *
from schemas import *
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import hashlib
from fastapi import HTTPException
import time


def hash_password(password):
    passwd_hash = hashlib.md5()
    passwd_hash.update(password.encode('utf-8'))
    return passwd_hash.hexdigest()


def create_user(db: Session, user: UserInDB):
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    user.hashed_password = hash_password(user.hashed_password)
    info = user.dict(exclude_unset=True)
    info['create_time'] = local_time
    if get_user(db, user.username) is None:
        user_obj = UserInfo(**info)
        db.add(user_obj)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail=f"Sorry, that username already exists.")
    return


def get_user(db: Session, username: str):
    return db.query(models.UserInfo).filter(models.UserInfo.username == username).first()


def active_user(db: Session, username: str):
    # 更新操作
    users = db.query(models.UserInfo).filter_by(username=username).first()  # 查询条件
    users.disabled = False  # 更新操作
    db.add(users)  # 添加到会话
    db.commit()  # 提交即保存到数据库
    return


def get_stock_code(db: Session, stock_name: str):
    return db.query(models.StockInfo).filter(models.StockInfo.stock_name == stock_name).first()


def get_plate_code(db: Session, plate_name: str):
    return db.query(models.PlateInfo).filter(models.PlateInfo.plate_name.like("%"+plate_name+"%")).first()

