from pydantic import BaseModel

class SaveRoomRequest(BaseModel):
    room_id: int | None = None
    sender_id: str
    receiver_id: list