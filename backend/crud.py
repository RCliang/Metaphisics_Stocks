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


def get_stock_code(db: Session, stock_name: str):
    stock_info = db.query(models.StockInfo).filter(models.StockInfo.stock_name == stock_name).first()
    return stock_info.stock_code if stock_info else None

def get_plate_code(db: Session, plate_name: str):
    return db.query(models.PlateInfo).filter(models.PlateInfo.plate_name.like("%"+plate_name+"%")).first()

