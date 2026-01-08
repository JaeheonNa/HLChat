from pydantic import BaseModel


class AddTempUserRequest(BaseModel):
    user_id: str


class ChangeUserPasswordRequest(BaseModel):
    user_id: str
    password: str
    new_password: str


class LogInRequest(BaseModel):
    user_id: str
    password: str

class ChangeUsernameRequest(BaseModel):
    username: str