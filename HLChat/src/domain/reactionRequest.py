from pydantic import BaseModel


class ToggleReactionRequest(BaseModel):
    room_id: int
    message_ln_no: int
    user_id: str
    user_name: str
    reaction_type: str
