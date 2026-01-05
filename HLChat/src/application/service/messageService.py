from fastapi import Depends
from starlette.websockets import WebSocket
from typing_extensions import override

from adapter.output.messagePersistenceAdapter import RequestMessagePersistenceAdapter
from adapter.output.redisStreamProducer import RedisStreamProducer
from adapter.output.redisStreamSubscriber import RedisStreamSubscriber
from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from application.port.output.messagePort import MongoMessagePort, RedisPublishMessagePort, RedisSubscribeMessagePort
from application.port.output.roomPort import MongoRoomPort
from domain.request import SendMessageRequest
from application.port.input.messageUsecase import SaveAndSendMessageUsecase, \
    FindSavedMessageUsecase, SubscribeMessageUsecase


class SaveAndSendMessageService(SaveAndSendMessageUsecase):

    def __init__ (self,
                  mongoMessagePort: MongoMessagePort = Depends(RequestMessagePersistenceAdapter),
                  mongoRoomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                  redisMessagePort: RedisPublishMessagePort = Depends(RedisStreamProducer)):
        self.mongoMessagePort = mongoMessagePort
        self.mongoRoomPort = mongoRoomPort
        self.redisMessagePort = redisMessagePort

    async def saveMessage(self, request: SendMessageRequest):
        if request.room_id is None:
            request.room_id = await self.mongoRoomPort.save_room(request)
        await self.mongoMessagePort.saveMessage(request)

    def sendMessage(self, request: SendMessageRequest):
        self.redisMessagePort.publishMessage(
            str(request.room_id),
            {
                "sender": request.sender_id,
                "message": request.message
            }
        )

    @override
    async def saveAndSendMessage(self, request: SendMessageRequest):
        await self.saveMessage(request)
        self.sendMessage(request)

class FindSavedMessageService(FindSavedMessageUsecase):
    def __init__ (self,
                  mongoMessagePort: MongoMessagePort = Depends(RequestMessagePersistenceAdapter)
    ):
        self.mongoMessagePort = mongoMessagePort

    @override
    async def findSavedMessage(self, room_id: int, websocket: WebSocket):
        latest_messages = await self.mongoMessagePort.findSavedMessage(room_id)
        # latest_messages = list(cursor)
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