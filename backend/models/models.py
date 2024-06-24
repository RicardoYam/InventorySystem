from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, DateTime, CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
import datetime

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

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


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    salt: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Customer(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    level: Mapped[CustomerLevel] = mapped_column(nullable=False)
    point: Mapped[int] = mapped_column(nullable=False)
    create_time = mapped_column(DateTime(timezone=True), default=datetime.datetime.now)

    def __repr__(self):
        return f'<Customer {self.username}>'

class Order(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoIncreament=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customer.id'), nullable=False)
    create_time = mapped_column(DateTime(timezone=True), default=datetime.datetime.now)
    method: Mapped[PaymentMethod] = mapped_column(nullable=False)
    total: Mapped[float] = mapped_column(nullable=False)

    customer = db.relationship('Customer', backref=db.backref('order', lazy=True))

    def __repr__(self):
        return f'<Order {self.id}>'