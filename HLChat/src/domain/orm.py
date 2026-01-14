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