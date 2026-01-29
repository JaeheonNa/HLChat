from pydantic import BaseModel

class SendMessageRequest(BaseModel):
    room_id: int | None = None
    sender_id: str
    message: str # 파일 전송의 경우 파일명.
    message_type: str
    file_id: int | None = None
    file_path: str | None = None