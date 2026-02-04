from typing import List

from pydantic import BaseModel

class SaveRoomRequest(BaseModel):
    room_id: int | None = None
    members: List[str]
    room_name: str | None = None

class UpdateLastReadRequest(BaseModel):
    room_id: int
    message_ln_no: int

class CreateGroupRoomRequest(BaseModel):
    members: List[str]
    room_name: str | None = None

class InviteMembersRequest(BaseModel):
    members: List[str]