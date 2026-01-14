from typing import List

from pydantic import BaseModel

class SaveRoomRequest(BaseModel):
    room_id: int | None = None
    members: List[str]
    room_name: str | None = None