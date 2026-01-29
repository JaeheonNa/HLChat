from datetime import datetime
from typing import List, Dict, Optional

from odmantic import AIOEngine, Model

class HLChatRoom(Model):
    room_id: int
    room_name: str
    members: List[str]
    created_at: datetime
    last_update_at: datetime
    last_update_message: Optional[str] = None
    last_update_message_ln_no: Optional[int] = None
    last_update_user_id: Optional[str] = None
    last_read: Dict[str, int] # [userId, message_ln_no]
    # Collection Name 지정.
    model_config = {"collection": "rooms"}

class HLChatMessage(Model):
    room_id: int
    message_ln_no: int
    sender: str
    message: str
    message_type: str
    created_at: datetime
    file_id: Optional[int] = None
    file_path: Optional[str] = None
    # Collection Name 지정.
    model_config = {"collection": "messages"}

# MongoDB: db -> collection -> document
# MySQL: db -> table -> row
