import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Enum

from ..database import Base


class UserRole(enum.Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT.value)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))