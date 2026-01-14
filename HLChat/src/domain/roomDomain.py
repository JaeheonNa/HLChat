from datetime import datetime
from typing import List


class RoomDomain():
    def __init__(self, roomId: int, roomName: str, members: List[str], created_at: datetime):
        self.roomId = roomId
        self.roomName = roomName
        self.members = members
        self.created_at = created_at
