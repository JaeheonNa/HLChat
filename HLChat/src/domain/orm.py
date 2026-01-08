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

    @classmethod
    def verifyPassword(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(encoding), hashed_password.encode(encoding)
        )

    @classmethod
    def hashedPassword(cls, plain_password: str) -> str:
        hashedPassword: bytes = bcrypt.hashpw(
            plain_password.encode(encoding), bcrypt.gensalt()
        )
        return hashedPassword.decode(encoding)

    @classmethod
    def createTempUser(cls, request: AddTempUserRequest):
        hashedPassword = cls.hashedPassword(request.user_id)
        return cls(user_id=request.user_id, password=hashedPassword, active=False)

    def createJWT(self):
        return jwt.encode(
            {"sub": self.user_id, "exp": datetime.now() + timedelta(days=1)},  # unique id
            secret_key,
            algorithm=jwt_algorithm,
        )

    @classmethod
    def decodeJWT(self, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token, secret_key, algorithms=[jwt_algorithm]
        )
        # Todo check expired
        return payload["sub"]