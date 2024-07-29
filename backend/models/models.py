from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List
from typing import Optional
import enum
import datetime

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "Admin"
    USER = "User"


class CustomerLevel(enum.Enum):
    SILVER = "Silver"
    Gold = "Gold"
    PLATINUM = "Platinum"


class PaymentMethod(enum.Enum):
    ALIPAY = "AliPay"
    WECHAT = "WeChat"
    CREDITCARD = "CreditCard"
    TRANSFER = "Transfer"
    CASH = "Cash"
    
    
class ProductSize(enum.Enum):
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"
    EXTRALARGE = "XL"


class User(db.Model):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    salt: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False)
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    
class Customer(db.Model):
    __tablename__ = "customer"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    level: Mapped[CustomerLevel] = mapped_column(nullable=False)
    point: Mapped[int] = mapped_column(nullable=False)
    credit: Mapped[int] = mapped_column(nullable=True)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.username}>"


class Order(db.Model):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer.id"))
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    method: Mapped[PaymentMethod] = mapped_column(nullable=False)
    total: Mapped[float] = mapped_column(nullable=False)

    customer: Mapped[Optional["Customer"]] = relationship(back_populates="orders")
    product_orders: Mapped[List["Product_order"]] = relationship(back_populates="order")

    def __repr__(self):
        return f"<Order {self.id}>"
    
    
class Product_order(db.Model):
    __tablename__ = "product_order"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    
    order: Mapped["Order"] = relationship(back_populates="product_orders")
    product: Mapped["Product"] = relationship(back_populates="product_orders")
    
    def __repr__(self):
        return f"<Product_order {self.id}>"
    
    
class Product(db.Model):
    __tablename__ = "product"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    color: Mapped[str] = mapped_column(nullable=False)
    size: Mapped[ProductSize] = mapped_column(nullable=False)
    purchased_price: Mapped[float] = mapped_column(nullable=False)
    selling_price: Mapped[float] = mapped_column(nullable=False)
    image_name: Mapped[str] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    image_type: Mapped[str] = mapped_column(nullable=True)
    
    product_orders: Mapped[List["Product_order"]] = relationship(back_populates="product")
    stocks: Mapped[List["Stock"]] = relationship(back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.id}>"
    
    
class Stock(db.Model):
    __tablename__ = "stock"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product.id"))
    quantity: Mapped[int] = mapped_column(nullable=False)
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    product: Mapped[Optional["Product"]] = relationship(back_populates="stocks")
    
    def __repr__(self):
        return f"<Stock {self.id}>"