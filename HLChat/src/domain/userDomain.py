from typing import Optional

from config import secret_key, encoding, jwt_algorithm
import bcrypt
from jose import jwt

from domain.orm import User
from domain.userRequest import AddTempUserRequest, RegisterRequest, KakaoRegisterRequest
from datetime import datetime, timedelta

PASSWORD_EXPIRY_DAYS = 90


class UserDomain():
    def __init__(
        self,
        userId: str,
        password: str,
        username: str | None,
        active: bool,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        phone_verified: bool = False,
        profile_image: Optional[str] = None,
        provider: str = 'LOCAL',
        provider_id: Optional[str] = None,
        password_changed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.userId = userId
        self.password = password
        self.username = username
        self.active = active
        self.email = email
        self.phone = phone
        self.phone_verified = phone_verified
        self.profile_image = profile_image
        self.provider = provider
        self.provider_id = provider_id
        self.password_changed_at = password_changed_at
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def verifyPassword(cls, plain_password: str, hashed_password: str) -> bool:
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

    @classmethod
    def createUser(cls, request: RegisterRequest):
        hashedPassword = cls.hashedPassword(request.password)
        now = datetime.now()
        return cls(
            userId=request.user_id,
            password=hashedPassword,
            username=request.user_name,
            active=True,
            email=request.email,
            phone=request.phone,
            password_changed_at=now,
            created_at=now,
            updated_at=now
        )

    @classmethod
    def createKakaoUser(cls, request: KakaoRegisterRequest):
        import uuid
        random_password = cls.hashedPassword(uuid.uuid4().hex)
        now = datetime.now()
        return cls(
            userId=request.user_id,
            password=random_password,
            username=request.user_name,
            active=True,
            email=request.email,
            phone=request.phone,
            profile_image=request.profile_image,
            provider=request.provider,
            provider_id=request.provider_id,
            password_changed_at=now,
            created_at=now,
            updated_at=now
        )

    def isPasswordExpired(self) -> bool:
        if self.password_changed_at is None:
            return True
        days_since_change = (datetime.now() - self.password_changed_at).days
        return days_since_change >= PASSWORD_EXPIRY_DAYS

    def createJWT(self):
        return jwt.encode(
            {"sub": self.userId, "exp": datetime.now() + timedelta(days=1)},
            secret_key,
            algorithm=jwt_algorithm,
        )

    @classmethod
    def decodeJWT(cls, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token, secret_key, algorithms=[jwt_algorithm]
        )
        return payload["sub"]

    def setUsername(self, username: str):
        self.username = username

    def setPassword(self, password: str):
        self.password = password
        self.password_changed_at = datetime.now()

    def setActive(self, active: bool):
        self.active = active

    def setEmail(self, email: str):
        self.email = email

    def setPhone(self, phone: str):
        self.phone = phone

    def setProfileImage(self, profile_image: str):
        self.profile_image = profile_image

    def toEntity(self):
        return User(
            user_id=self.userId,
            password=self.password,
            user_name=self.username,
            active=self.active,
            email=self.email,
            phone=self.phone,
            phone_verified=self.phone_verified,
            profile_image=self.profile_image,
            provider=self.provider,
            provider_id=self.provider_id,
            password_changed_at=self.password_changed_at,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
