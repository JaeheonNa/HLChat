from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
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

class RoomSchema(BaseModel):
    roomId: int = Field(alias="room_id")
    roomName: str = Field(alias="room_name")
    members: List[str] | None = Field(default=None)
    createdAt: datetime = Field(alias="created_at")
    lastUpdateAt: datetime = Field(alias="last_update_at")
    lastUpdateMessage: Optional[str] = Field(alias="last_update_message", default=None)
    lastUpdateMessageLnNo: Optional[int] = Field(alias="last_update_message_ln_no", default=None)
    lastUpdateUserId: Optional[str] = Field(alias="last_update_user_id", default=None)
    lastRead: Dict[str, int] = Field(alias="last_read")

    # sqlalchemy의 orm 객체를 받아서 매핑해주는 설정.
    model_config = ConfigDict(from_attributes=True,
                              populate_by_name=True)

class RoomListSchema(BaseModel):
    rooms: List[RoomSchema]