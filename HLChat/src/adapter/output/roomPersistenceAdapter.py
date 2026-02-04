from typing import override, List

from fastapi import Depends, HTTPException

from application.port.output.roomPort import MongoRoomPort
from common.mongo import MongoDB
from domain.messageRequest import SendMessageRequest
from domain.odm import HLChatRoom
from datetime import datetime

from common.mongo import getMonoDB
from domain.response import RoomListSchema, RoomSchema
from domain.roomDomain import RoomDomain
from domain.roomRequest import SaveRoomRequest, UpdateLastReadRequest


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
    async def createRoom(self, request: SaveRoomRequest) -> int:
        new_room_id = await self.findRoomId()
        lastRead = dict()
        for member in request.members:
            lastRead[member] = 0
        room = HLChatRoom(room_id=new_room_id,
                          members=request.members,
                          room_name=request.room_name,
                          created_at=datetime.now(),
                          last_update_at=datetime.now(),
                          last_update_message=None,
                          last_update_message_ln_no=None,
                          last_update_user_id=None,
                          last_read=lastRead)
        await self.mongo_db.save(room)
        return new_room_id

    @override
    async def findRoomIdByUserIdAndFriendId(self, user_id: str, friend_id: str) -> int | None:
        collection = self.mongo_db.get_collection(HLChatRoom)
        memberSet = {user_id, friend_id}
        memberList = list(memberSet)
        room = await collection.find_one({
            "members":{"$all": memberList},
            "$expr": {"$eq": [{"$size": "$members"}, len(memberList)]}
        })
        if room is None:
            return None
        else:
            return room.get('room_id')


    @override
    async def findRoomByRoomId(self, room_id: int) -> RoomDomain:
        room: HLChatRoom = await self.mongo_db.find_one(HLChatRoom,
                                                    HLChatRoom.room_id == room_id)
        if room:
            return RoomDomain(roomId=room.room_id,
                              roomName=room.room_name,
                              members=room.members,
                              created_at=room.created_at)
        else:
            raise HTTPException(status_code=404, detail="Room not found")

    @override
    async def updateRoomLastInfo(self, request: SendMessageRequest, newMessageLnNo: int):
        room: HLChatRoom = await self.mongo_db.find_one(HLChatRoom,
                                                    HLChatRoom.room_id == request.room_id)
        room.last_update_at = datetime.now()
        room.last_update_message_ln_no = newMessageLnNo
        room.last_update_message = request.message
        room.last_update_user_id = request.sender_id
        room.last_read = {
            **room.last_read,
            request.sender_id: newMessageLnNo
        }

        await self.mongo_db.save(room)
        return RoomSchema.model_validate(room)

    @override
    async def findAllRoomsByUserId(self, userId: str):
        collection = self.mongo_db.get_collection(HLChatRoom)
        roomList: List[HLChatRoom] = await (collection.find({"members": {"$in": [userId]}})
                                                        .sort("last_update_at", -1)
                                                        .to_list())
        return RoomListSchema(rooms=[RoomSchema.model_validate(room) for room in roomList])

    @override
    async def updateLastRead(self, request: UpdateLastReadRequest, userId: str):
        room: HLChatRoom = await self.mongo_db.find_one(HLChatRoom, HLChatRoom.room_id == request.room_id)
        room.last_read = {
            **room.last_read,
            userId: request.message_ln_no
        }
        await self.mongo_db.save(room)

    @override
    async def updateRoomMember(self, roomDomain: RoomDomain):
        room: HLChatRoom = await self.mongo_db.find_one(HLChatRoom, HLChatRoom.room_id == roomDomain.roomId)
        room.members = roomDomain.members
        await self.mongo_db.save(room)