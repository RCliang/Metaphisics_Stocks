from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:BornIn^2021@124.221.163.154:5432/futu_base"

engine = create_engine(  # connect_args只有配置sqlite时才使用
    SQLALCHEMY_DATABASE_URL, encoding='utf-8', echo=True#, connect_args={'check_same_thread':False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=True)

# 创建基本的映射类
Base = declarative_base(bind=engine, name='Base')