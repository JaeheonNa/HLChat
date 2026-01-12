from typing import override

from fastapi import Depends, HTTPException
from odmantic.query import match

from application.port.output.roomPort import MongoRoomPort
from common.mongo import MongoDB
from domain.odm import HLChatRoom
from domain.messageRequest import SendMessageRequest
from datetime import datetime

from common.mongo import getMonoDB
from domain.roomDomain import RoomDomain
from domain.roomRequest import SaveRoomRequest


class RequestRoomPersistenceAdapter(MongoRoomPort):
    def __init__(self, mongo_db: MongoDB = Depends(getMonoDB)):
        self.mongo_db = mongo_db.engine
    @override
    async def findRoomId(self) -> int:
        room = await self.mongo_db.find(HLChatRoom,
                                        sort=HLChatRoom.room_id.desc(),
                                        limit=1)
        if room:
            return room[0].room_id + 1
        else:
            return 1

    @override
    async def saveRoom(self, request: SaveRoomRequest) -> int:
        new_room_id = await self.findRoomId()

        room = HLChatRoom(room_id=new_room_id,
                          members=[request.sender_id, *[receiver for receiver in request.receiver_id]],
                          created_at=datetime.now())
        await self.mongo_db.save(room)
        return new_room_id

    @override
    async def findRoomIdByUserIdAndFriendId(self, user_id: str, friend_id: str) -> int | None:
        collection = self.mongo_db.get_collection(HLChatRoom)
        room = await collection.find_one({
            "members":{"$all": [user_id, friend_id]},
            "$expr": {"$eq": [{"$size": "$members"}, 2]}
        })
        if room is None:
            request = SaveRoomRequest(room_id=None,
                                         sender_id=user_id,
                                         receiver_id=[friend_id])
            return await self.saveRoom(request)
        else:
            return room.get('room_id')


    @override
    async def findRoomByRoomId(self, room_id: int) -> RoomDomain:
        room: HLChatRoom = await self.mongo_db.find_one(HLChatRoom,
                                                    HLChatRoom.room_id == room_id)
        if room:
            return RoomDomain(roomId=room.room_id,
                   members=room.members,
                   created_at=room.created_at)
        else:
            raise HTTPException(status_code=404, detail="Room not found")
