from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from pymongo import MongoClient
from redis import Redis

from database.mongo import get_mongo_client
from schema.request import SendMessageRequest
from service.messageService import MessageHandler
from service.redisStream import RedisStreamProducer, RedisStreamSubscriber
from channel import get_redis_producer, get_redis_subscriber

app = FastAPI()

@app.post("/HLChat", status_code=200)
def sendMessage(
        request: SendMessageRequest,
        message_handler: MessageHandler = Depends(MessageHandler)
):
    message_handler.handleMessage(request)

@app.websocket("/HLChat/{room_id}")
async def websocket_endpoint(room_id: str,
                             websocket: WebSocket,
                             message_handler: MessageHandler = Depends(MessageHandler),
                             redis_subscriber: RedisStreamSubscriber = Depends(RedisStreamSubscriber)
):
    await websocket.accept()
    await message_handler.getSavedMessage(room_id=room_id, websocket=websocket)
    await redis_subscriber.subscribe(room_id=room_id, websocket=websocket)

