from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    userId: str = Field(alias="user_id")
    username: str | None = Field(default=None, alias="user_name")
    active: bool
    profile_image: Optional[str] = Field(default=None, alias="profile_image")

    # sqlalchemy의 orm 객체를 받아서 매핑해주는 설정.
    model_config = ConfigDict(from_attributes=True,
                              populate_by_name=True)

class UserListSchema(BaseModel):
    users: List[UserSchema]

class JWTResponse(BaseModel):
    access_token: str
    username: str
    password_expired: bool = False


class MyProfileResponse(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    provider: str = 'LOCAL'


class ProfileImageResponse(BaseModel):
    image_url: str

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

class RoomBaseInfoSchema(BaseModel):
    roomId: int = Field(alias="room_id")
    members: List[str] | None = Field(default=None)

class RoomListSchema(BaseModel):
    rooms: List[RoomSchema]

class FileSchema(BaseModel):
    fileId: int = Field(alias="file_id")
    fileName: str = Field(alias="file_name")
    roomId: int = Field(alias="room_id")
    senderId: str = Field(alias="sender_id")
    filePath: str = Field(alias="file_path")
    createdAt: datetime = Field(alias="created_at")

    # sqlalchemy의 orm 객체를 받아서 매핑해주는 설정.
    model_config = ConfigDict(from_attributes=True,
                              populate_by_name=True)

class FileListSchema(BaseModel):
    files: List[FileSchema]


class KakaoAuthUrlResponse(BaseModel):
    auth_url: str


class KakaoCallbackResponse(BaseModel):
    requires_registration: bool
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    provider_id: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    existing_user_id: Optional[str] = None
    existing_user_name: Optional[str] = None