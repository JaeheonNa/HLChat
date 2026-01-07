from typing import List

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    user_id: str
    user_name: str | None = None
    active: bool

    # sqlalchemy의 orm 객체를 받아서 매핑해주는 설정.
    model_config = ConfigDict(from_attributes=True)

class UserListSchema(BaseModel):
    users: List[UserSchema]

class JWTResponse(BaseModel):
    access_token: str