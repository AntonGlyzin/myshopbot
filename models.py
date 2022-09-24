from sqlalchemy import Integer, String, \
    Column, DateTime, ForeignKey, SmallInteger, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from config import CURRENCY

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    email = Column(String(200))
    phone_number = Column(String(20))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_on = Column(DateTime, default=datetime.now)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_banned = Column(Boolean, default=False)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    photo = Column(String(250))
    description = Column(Text)
    price =  Column(Integer, nullable=False)
    currency = Column(String(10), default=CURRENCY)
    quantity = Column(SmallInteger)
    is_active = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer(), primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), index=True)
    amount =  Column(Integer, nullable=False)
    payd =  Column(Integer, default=0)
    currency = Column(String(10), default=CURRENCY)
    date = Column(DateTime, default=datetime.now)
    status = Column(Boolean, default=False)
    customer = relationship('Customer', backref='orders')
    products = relationship('ProductOrder', backref='order')

class ProductOrder(Base):
    __tablename__ = 'product_order'
    id = Column(Integer(), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    order_id = Column(Integer, ForeignKey('order.id'))
    quantity = Column(SmallInteger, nullable=False)
    currency = Column(String(10), default=CURRENCY)
    amount =  Column(Integer, nullable=False)
    product = relationship('Product')

class Basket(Base):
    __tablename__ = 'basket'
    id = Column(Integer(), primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), index=True)
    product_id = Column(Integer, ForeignKey('product.id'), index=True)
    quantity = Column(SmallInteger, nullable=False)
    product = relationship('Product', backref='items_basket')
    customer = relationship('Customer', backref='items_basket')

