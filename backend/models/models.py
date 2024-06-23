from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, DateTime, CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=True)
    salt = db.Column(db.String(29), nullable=True)
    password = db.Column(db.String(128), nullable=True)
    role = db.Column(Enum(UserRole), nullable=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
