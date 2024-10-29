from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, ForeignKey, func, Boolean

from database import Base


class StockInfo(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    stock_code = Column(String(100), unique=True, nullable=False, comment="股票代码")
    stock_name = Column(String(100), nullable=False, comment="股票中文名")
    exchange_type = Column(String(100), nullable=False, comment="所属市场")
    delisting = Column(Boolean, nullable=False, comment="是否退市")
    listing_date = Column(String(20), nullable=False)
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    mapper = {"order_by": id}
    comment = Column(String(200))

    def __repr__(self):
        return f"{self.stock_code}_{self.stock_name}"

class PlateInfo(Base):
    __tablename__ = "plates"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    plate_code = Column(String(100), unique=True, nullable=False, comment="板块代码")
    plate_name = Column(String(100), nullable=False, comment="板块中文名")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    mapper = {"order_by": id}
    comment = Column(String(200))

    def __repr__(self):
        return f"{self.plate_code}_{self.plate_name}"
