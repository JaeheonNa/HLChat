from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(String, primary_key=True)
    password = Column(String)
    user_name = Column(String)
    active = Column(Boolean)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    phone_verified = Column(Boolean, default=False)
    profile_image = Column(String, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, active={self.active})"

class File(Base):
    __tablename__ = "file"
    file_id = Column(Integer, primary_key=True, autoincrement=True)
    file_name: str = Column(String)
    room_id: int = Column(Integer)
    sender_id: str = Column(String)
    file_path: str = Column(String)
    created_at: datetime = Column(default=datetime.now)