from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    password = Column(String)
    user_name = Column(String)
    active = Column(Boolean)

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