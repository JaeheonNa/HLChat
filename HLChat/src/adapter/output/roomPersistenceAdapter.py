from typing import override

from fastapi import Depends

from application.port.output.roomPort import MongoRoomPort
from common.mongo import MongoDB
from domain.odm import HLChatRoom
from domain.request import SendMessageRequest
from datetime import datetime

from common.mongo import getMonoDB


class RequestRoomPersistenceAdapter(MongoRoomPort):
    def __init__(self, mongo_db: MongoDB = Depends(getMonoDB)):
        self.mongo_db = mongo_db.engine

    async def find_room_id(self, request: SendMessageRequest) -> int:
        room = await self.mongo_db.find(HLChatRoom,
                                        sort=HLChatRoom.room_id.desc(),
                                        limit=1)
        if room:
            return room[0].room_id + 1
        else:
            return 1

    @override
    async def save_room(self, request: SendMessageRequest) -> int:
        new_room_id = await self.find_room_id(request)

        room = HLChatRoom(room_id=new_room_id,
                          members=[request.sender_id, [receiver for receiver in request.receiver_id]],
                          created_at=datetime.now())
        await self.mongo_db.save(room)

        return new_room_id