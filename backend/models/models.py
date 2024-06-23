from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()