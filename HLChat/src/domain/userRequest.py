from typing import Optional
from pydantic import BaseModel


class AddTempUserRequest(BaseModel):
    user_id: str


class ChangeUserPasswordRequest(BaseModel):
    user_id: str
    password: str
    user_name: Optional[str] = None
    new_password: str


class LogInRequest(BaseModel):
    user_id: str
    password: str


class ChangeUsernameRequest(BaseModel):
    username: str


class RegisterRequest(BaseModel):
    user_id: str
    password: str
    user_name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class UpdateMyProfileRequest(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None