from typing import List

from fastapi import Depends, HTTPException
from typing_extensions import override

from adapter.output.redisStreamSubscriber import RedisStreamSubscriber
from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.input.roomUsecase import FindRoomIdUsecase, FindAllRoomsByUserIdUsecase, \
    FindAndSendAllRoomsLastMessagesUsecase, UpdateLastReadUsecase, CreateGroupRoomUsecase, UpdateRoomMemberUseCase, \
    FindRoomInfoByRoomIdUseCase, InviteMembersUsecase
from application.port.output.messagePort import RedisSubscribeMessagePort
from application.port.output.roomPort import MongoRoomPort
from application.port.output.userPort import MariaUserPort
from common.redisPubSubManager import RedisPubSubManager, get_connection_manager
from adapter.output.webSocket import WebSocketConnectionManager, get_websocket_connection_manager
from domain.response import RoomListSchema, RoomBaseInfoSchema, UserSchema, UserListSchema
from domain.roomDomain import RoomDomain
from domain.roomRequest import SaveRoomRequest, UpdateLastReadRequest, CreateGroupRoomRequest, InviteMembersRequest
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
                 mariaUserPort = Depends(RequestUserPersistenceAdapter),
                 connectionManager: WebSocketConnectionManager = Depends(get_websocket_connection_manager)):
        self.connectionManager = connectionManager
        self.roomPort = roomPort
        self.mariaUserPort = mariaUserPort

    @override
    async def findAndSendAllRoomsLastMessages(self, userId: str, roomList: RoomListSchema):
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
            await self.connectionManager.send_json(userId, response_body)

class UpdateLastReadService(UpdateLastReadUsecase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter)):
        self.roomPort = roomPort

    @override
    async def updateLastRead(self, request: UpdateLastReadRequest, access_token: str):
        user_id: str = UserDomain.decodeJWT(access_token)
        await self.roomPort.updateLastRead(request, user_id)

class CreateGroupRoomService(CreateGroupRoomUsecase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.roomPort = roomPort
        self.mariaUserPort = mariaUserPort

    @override
    async def createGroupRoom(self, request: CreateGroupRoomRequest, access_token: str):
        user_id: str = UserDomain.decodeJWT(access_token)
        memberSet = set(request.members)
        memberSet.add(user_id)
        memberList = list(memberSet)

        if request.room_name:
            roomName = request.room_name
        else:
            users: List[UserDomain] = await self.mariaUserPort.findUsersByUserIds(memberList)
            roomName = "|"
            for user in users:
                roomName += user.username + "|"

        saveRequest = SaveRoomRequest(room_id=None,
                                      members=memberList,
                                      room_name=roomName)
        return await self.roomPort.createRoom(saveRequest)

class UpdateRoomMemberService(UpdateRoomMemberUseCase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                 redisPubSubManager: RedisPubSubManager = Depends(get_connection_manager)):
        self.roomPort = roomPort
        self.redisPubSubManager = redisPubSubManager

    @override
    async def leaveRoom(self, roomId: int, userId: str):
        room: RoomDomain = await self.roomPort.findRoomByRoomId(roomId)
        room.members.remove(userId)
        await self.roomPort.updateRoomMember(room)
        subscriber: 'RedisStreamSubscriber' = self.redisPubSubManager.get_subscriber(userId)
        await subscriber.unsubscribe_from_room(str(roomId), userId)

    @override
    async def addRoomMember(self, roomId: int, userId: str, memberId: str):
        pass

class FindRoomInfoByRoomIdService(FindRoomInfoByRoomIdUseCase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter)
    ):
        self.roomPort = roomPort

    async def findRoomInfoByRoomId(self, roomId: int, userId: str):
        room: RoomDomain = await self.roomPort.findRoomByRoomId(roomId)
        if userId not in room.members:
            raise HTTPException(status_code=401, detail="Unauthorized(findRoomInfoByRoomId)")
        return RoomBaseInfoSchema(room_id=room.roomId,
                                members=room.members)

class InviteMembersService(InviteMembersUsecase):
    def __init__(self,
                 roomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter),
                 redisMessagePort: RedisSubscribeMessagePort = Depends(RedisStreamSubscriber)
    ):
        self.roomPort = roomPort
        self.mariaUserPort = mariaUserPort
        self.redisMessagePort = redisMessagePort

    async def inviteMembers(self, roomId: int, userId: str, request: InviteMembersRequest) -> UserListSchema:
        room: RoomDomain = await self.roomPort.findRoomByRoomId(roomId)
        if userId not in room.members:
            raise HTTPException(status_code=401, detail="Unauthorized(inviteMembers)")
        for invitee in request.members:
            if invitee in room.members:
                raise HTTPException(status_code=409, detail="User already invited")
        room.members.extend(request.members)
        await self.roomPort.updateRoomMember(room)
        userDomainList: List[UserDomain] = await self.mariaUserPort.findUsersByUserIds(request.members)
        userSchemaList = []
        for userDomain in userDomainList:
            userSchemaList.append(UserSchema(user_id=userDomain.userId,
                                             user_name=userDomain.username,
                                             active=userDomain.active,
                                             profile_image=userDomain.profile_image))
        for invitee in request.members:
            await self.redisMessagePort.subscribeXRoomMessage(room.roomId, invitee)
        return UserListSchema(users=userSchemaList)

