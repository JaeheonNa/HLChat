from pydantic import BaseModel

class SendMessageRequest(BaseModel):
    room_id: str | None
    sender_id: str
    receiver_id: list
    message: str
    message_type: str
