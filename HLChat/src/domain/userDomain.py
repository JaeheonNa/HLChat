from sqlalchemy.orm import Session

from config import secret_key, encoding, jwt_algorithm
import bcrypt
from jose import jwt

from domain.orm import User
from domain.userRequest import AddTempUserRequest
from datetime import datetime, timedelta

class UserDomain():
    def __init__(self, userId: str, password: str, username: str | None, active: bool):
        self.userId = userId
        self.password = password
        self.username = username
        self.active = active

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
        return cls(userId=request.user_id, password=hashedPassword, username=None, active=False)

    def createJWT(self):
        return jwt.encode(
            {"sub": self.userId, "exp": datetime.now() + timedelta(days=1)},  # unique id
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

    def setUsername(self, username: str):
        self.username = username

    def setPassword(self, password: str):
        self.password = password

    def setActive(self, active: bool):
        self.active = active

    def toEntity(self):
        return User(user_id=self.userId,
                    password=self.password,
                    user_name=self.username,
                    active=self.active)
