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
from domain.messageRequest import SendMessageRequest
from application.port.input.messageUsecase import SaveAndSendMessageUsecase, \
    FindSavedMessageUsecase, SubscribeMessageUsecase
from domain.odm import HLChatMessage
from domain.roomDomain import RoomDomain
from domain.roomRequest import SaveRoomRequest
from domain.userDomain import UserDomain


class SaveAndSendMessageService(SaveAndSendMessageUsecase):

    def __init__ (self,
                  mongoMessagePort: MongoMessagePort = Depends(RequestMessagePersistenceAdapter),
                  mongoRoomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                  redisMessagePort: RedisPublishMessagePort = Depends(RedisStreamProducer)):
        self.mongoMessagePort = mongoMessagePort
        self.mongoRoomPort = mongoRoomPort
        self.redisMessagePort = redisMessagePort

    async def saveMessage(self, request: SendMessageRequest):
        await self.mongoMessagePort.saveMessage(request)

    def sendMessage(self, request: SendMessageRequest):
        self.redisMessagePort.publishMessage(
            str(request.room_id),
            {
                "sender_id": request.sender_id,
                "message": request.message
            }
        )

    @override
    async def saveAndSendMessage(self, request: SendMessageRequest):
        await self.saveMessage(request)
        self.sendMessage(request)

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
    async def findSavedMessage(self, room_id: int, websocket: WebSocket):
        latest_messages: List[HLChatMessage] = await self.mongoMessagePort.findSavedMessage(room_id)
        for msg in latest_messages:
            response_body = {
                "sender_id": msg.sender,
                "message": msg.message
            }
            await websocket.send_json(response_body)

class SubscribeMessageService(SubscribeMessageUsecase):
    def __init__ (self,
                  redisMessagePort: RedisSubscribeMessagePort = Depends(RedisStreamSubscriber),
      ):
        self.redisMessagePort = redisMessagePort
    @override
    async def subscribeMessage(self, room_id: int, websocket: WebSocket):
        await self.redisMessagePort.subscribeMessage(str(room_id), websocket)