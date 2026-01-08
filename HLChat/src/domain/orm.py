from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from domain.userRequest import AddTempUserRequest
from config import secret_key, encoding, jwt_algorithm

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)
    password = Column(String)
    user_name = Column(String)
    active = Column(Boolean)

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, active={self.active})"