from datetime import datetime
from typing import List

from odmantic import AIOEngine, Model

class HLChatRoom(Model):
    room_id: int
    members: List[str]
    created_at: datetime

    # Collection Name 지정.
    model_config = {"collection": "rooms"}

class HLChatMessage(Model):
    room_id: int
    message_ln_no: int
    sender: str
    message: str
    created_at: datetime

    # Collection Name 지정.
    model_config = {"collection": "messages"}

# MongoDB: db -> collection -> document
# MySQL: db -> table -> row
