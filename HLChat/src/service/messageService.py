import datetime

import pymongo
from fastapi import Depends
from pymongo import MongoClient
from starlette.websockets import WebSocket
from typing_extensions import override

from database.databaseInterface import DatabaseInterface
from database.mongo import MongoDBClient
from schema.request import SendMessageRequest
from service.messageServiceInterface import MessageHandlerInterface
from service.pubSubInterface import Subscriber, Producer
from service.redisStream import RedisStreamProducer, RedisStreamSubscriber


class MessageHandler(MessageHandlerInterface):

    def __init__(self,
                 database_client: DatabaseInterface = Depends(MongoDBClient),
                 producer: Producer = Depends(RedisStreamProducer),
                 subscriber: Subscriber = Depends(RedisStreamSubscriber)
    ):
        self.database_client = database_client.get_client()
        self.producer = producer
        self.subscriber = subscriber

    def saveMessage(self, request: SendMessageRequest):
        db = self.database_client['local']
        if request.room_id is None:
            rooms = db['rooms']
            rooms.insert_one(
                {'room_id': 'room_001', # Todo 랜덤으로 생성하든, sequential하게 생성하든 해야 됨.
                 'message_type': request.message_type,
                 'members': [request.sender_id, [receiver for receiver in request.receiver_id]],
                 "created_at": datetime.datetime.now()}
            )
            request.room_id = 'room_001'

        messages = db['messages']
        messages.insert_one(
            {"room_id": request.room_id,
             "sender_id": request.sender_id,
             "message": request.message,
             "message_type": "text",
             "created_at": datetime.datetime.now()})

    def sendMessage(self, request: SendMessageRequest):
        self.producer.publish_message(
            request.room_id,
            {
            "sender" : request.sender_id,
            "message" : request.message
            }
        )

    @override
    def handleMessage(self, request: SendMessageRequest):
        self.saveMessage(request)
        self.sendMessage(request)

    @override
    async def getSavedMessage(self, room_id: str, websocket: WebSocket):
        db = self.database_client['local']
        collection = db['messages']
        cursor = (collection.find({'room_id': room_id})
                            .sort('created_at', pymongo.DESCENDING)
                            .limit(50))
        latest_messages = list(cursor)
        for msg in latest_messages:
            response_body = {
                "sender_id" : msg['sender_id'],
                "message" : msg['message'],
            }
            await websocket.send_json(response_body)

    @override
    async def subscribe_message(self, room_id: str, websocket: WebSocket):
        await self.subscriber.subscribe_message(room_id, websocket)