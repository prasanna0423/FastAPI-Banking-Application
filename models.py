from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(256), nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, default=0)
    address = Column(String(250), nullable=False)
    mobile_no = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(30), index=True, nullable=False)
    transaction_type = Column(String(30), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(250), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
