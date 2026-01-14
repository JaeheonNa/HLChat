from datetime import datetime
from typing import List

from fastapi import Depends
from starlette.websockets import WebSocket
from typing_extensions import override

from adapter.output.messagePersistenceAdapter import RequestMessagePersistenceAdapter
from adapter.output.redisStreamProducer import RedisStreamProducer
from adapter.output.redisStreamSubscriber import RedisStreamSubscriber
from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.output.messagePort import MongoMessagePort, RedisPublishMessagePort, RedisSubscribeMessagePort
from application.port.output.roomPort import MongoRoomPort
from application.port.output.userPort import MariaUserPort
from common.redisPubSubManager import RedisPubSubManager, get_connection_manager
from domain.messageRequest import SendMessageRequest
from application.port.input.messageUsecase import SaveAndSendMessageUsecase, \
    FindSavedMessageUsecase, SubscribeMessageUsecase
from domain.odm import HLChatMessage
from domain.response import RoomListSchema, RoomSchema
from domain.roomDomain import RoomDomain


class SaveAndSendMessageService(SaveAndSendMessageUsecase):

    def __init__ (self,
                  mongoMessagePort: MongoMessagePort = Depends(RequestMessagePersistenceAdapter),
                  mongoRoomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                  redisMessagePort: RedisPublishMessagePort = Depends(RedisStreamProducer),
                  redisPubSubManager: RedisPubSubManager = Depends(get_connection_manager),):
        self.mongoMessagePort = mongoMessagePort
        self.mongoRoomPort = mongoRoomPort
        self.redisMessagePort = redisMessagePort
        self.redisPubSubManager = redisPubSubManager

    async def saveMessage(self, request: SendMessageRequest):
        return await self.mongoMessagePort.saveMessage(request)

    async def sendMessage(self, request: SendMessageRequest, newMessageLnNo: int, roomSchema: RoomSchema):
        for member in roomSchema.members:
            subscriber = self.redisPubSubManager.get_subscriber(member)
            if subscriber is not None:
                await self.redisPubSubManager.add_room_subscription(member, str(roomSchema.roomId))

        await self.redisMessagePort.publishMessage(
            str(request.room_id),
            {
                "lastUserId": request.sender_id,
                "roomName": roomSchema.roomName,
                "lastUpdateMessage": roomSchema.lastUpdateMessage,
                "lastUpdateAt": roomSchema.lastUpdateAt.isoformat(),
                "lastUpdateMessageLnNo": newMessageLnNo,
                "lastRead": roomSchema.lastRead
            }
        )

    @override
    async def saveAndSendMessage(self, request: SendMessageRequest):
        newMessageLnNo: int = await self.saveMessage(request)
        roomSchema: RoomSchema = await self.mongoRoomPort.updateRoomLastInfo(request, newMessageLnNo)
        await self.sendMessage(request, newMessageLnNo, roomSchema)

class FindSavedMessageService(FindSavedMessageUsecase):
    def __init__ (self,
                  mongoMessagePort: MongoMessagePort = Depends(RequestMessagePersistenceAdapter),
                  mongoRoomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                  mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mongoMessagePort = mongoMessagePort
        self.mongoRoomPort = mongoRoomPort
        self.mariaUserPort = mariaUserPort

    @override
    async def findSavedMessagesByRoomId(self, room_id: int):
        room: RoomDomain = await self.mongoRoomPort.findRoomByRoomId(room_id)
        latestMessages: List[HLChatMessage] = await self.mongoMessagePort.findSavedMessage(room_id)
        responseBodyList = list()
        for msg in latestMessages:
            response_body = {
                "roomId": msg.room_id,
                "messageData": {
                    "lastUserId": msg.sender,
                    "roomName": room.roomName,
                    "lastUpdateMessage": msg.message,
                    "unreadMessageCount": None,
                    "lastUpdateAt": msg.created_at.isoformat(),
                    "lastUpdateMessageLnNo": msg.message_ln_no
                }
            }
            responseBodyList.append(response_body)
        return responseBodyList


class SubscribeMessageService(SubscribeMessageUsecase):
    def __init__ (self,
                  redisMessagePort: RedisSubscribeMessagePort = Depends(RedisStreamSubscriber)):
        self.redisMessagePort = redisMessagePort
    @override
    async def subscribeMessage(self, roomList: RoomListSchema, websocket: WebSocket, userId: str):
        await self.redisMessagePort.subscribeMessage(roomList, websocket, userId)