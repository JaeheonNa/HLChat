from typing import List

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    def __init__(self, userId: str, username: str, active: bool):
        self.userId = userId
        self.username = username
        self.active = active

    userId: str = Field(alias="user_id")
    username: str | None = Field(default=None, alias="user_name")
    active: bool

    # sqlalchemy의 orm 객체를 받아서 매핑해주는 설정.
    model_config = ConfigDict(from_attributes=True,
                              populate_by_name=True)

class UserListSchema(BaseModel):
    users: List[UserSchema]

class JWTResponse(BaseModel):
    access_token: str
    username: str