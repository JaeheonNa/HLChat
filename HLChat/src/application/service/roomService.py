from typing import List

from fastapi import Depends
from starlette.websockets import WebSocket
from typing_extensions import override

from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.input.roomUsecase import FindRoomIdUsecase, FindAllRoomsByUserIdUsecase, \
    FindAndSendAllRoomsLastMessagesUsecase, UpdateLastReadUsecase
from application.port.output.roomPort import MongoRoomPort
from application.port.output.userPort import MariaUserPort
from domain.response import RoomListSchema
from domain.roomDomain import RoomDomain
from domain.roomRequest import SaveRoomRequest, UpdateLastReadRequest
from domain.userDomain import UserDomain


class FindRoomIdService(FindRoomIdUsecase):

    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.roomPort = roomPort
        self.mariaUserPort = mariaUserPort

    @override
    async def findRoomIdByUserIdAndFriendId(self,
                                      user_id: str,
                                      friend_id: str
    ):
        roomId: int | None = await self.roomPort.findRoomIdByUserIdAndFriendId(user_id, friend_id)
        if roomId is not None:
            return roomId
        else:
            # room이 없으면 새로 생성 후 리턴
            memberSet = {user_id, friend_id}
            memberList = list(memberSet)
            return await self.createRoom(memberList)


    async def createRoom(self, memberList: List[str]):
        users: List[UserDomain] = await self.mariaUserPort.findUsersByUserIds(memberList)
        roomName = "|"
        for user in users:
            roomName += user.username + "|"
        print("roomName:", roomName)
        request = SaveRoomRequest(room_id=None,
                                  members=memberList,
                                  room_name=roomName)
        return await self.roomPort.createRoom(request)

class FindAllRoomsByUserIdService(FindAllRoomsByUserIdUsecase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter)):
        self.roomPort = roomPort

    @override
    async def findAllRoomsByUserId(self, userId: str):
         return await self.roomPort.findAllRoomsByUserId(userId)

class FindAndSendAllRoomsLastMessagesService(FindAndSendAllRoomsLastMessagesUsecase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                 mariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.roomPort = roomPort
        self.mariaUserPort = mariaUserPort

    @override
    async def findAndSendAllRoomsLastMessages(self, userId: str, roomList: RoomListSchema, websocket: WebSocket):
        for room in roomList.rooms:
            unreadMsgCnt = 0
            if room.lastUpdateMessageLnNo:
                unreadMsgCnt = room.lastUpdateMessageLnNo - room.lastRead.get(userId, 0)

            response_body = {
                "roomId": room.roomId,
                "messageData": {
                    "lastUserId": room.lastUpdateUserId,
                    "roomName": room.roomName,
                    "lastUpdateMessage": room.lastUpdateMessage,
                    "unreadMessageCount": unreadMsgCnt,
                    "lastUpdateAt": room.lastUpdateAt.isoformat(),
                    "lastUpdateMessageLnNo": room.lastUpdateMessageLnNo
                }
            }

            await websocket.send_json(response_body)

class UpdateLastReadService(UpdateLastReadUsecase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter)):
        self.roomPort = roomPort

    @override
    async def updateLastRead(self, request: UpdateLastReadRequest, access_token: str):
        user_id: str = UserDomain.decodeJWT(access_token)
        await self.roomPort.updateLastRead(request, user_id)
