from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from pymongo import MongoClient
from redis import Redis

from database.mongo import get_mongo_client
from schema.request import SendMessageRequest
from service.messageService import MessageHandler
from service.redisStream import RedisStreamProducer, RedisStreamSubscriber
from channel import get_redis_publisher, get_redis_subscriber

app = FastAPI()

@app.post("/HLChat", status_code=200)
def sendMessage(
        request: SendMessageRequest,
        mongo_client: MongoClient = Depends(get_mongo_client),
        redis_publisher: Redis = Depends(get_redis_publisher)
):
    redis_producer = RedisStreamProducer(redis_publisher)
    message_handelr = MessageHandler(mongo_client, redis_producer)
    message_handelr.handleMessage(request)

@app.websocket("/HLChat/{room_id}")
async def websocket_endpoint(websocket: WebSocket,
                             room_id: str,
                             mongo_client: MongoClient = Depends(get_mongo_client),
                             redis_publisher: Redis = Depends(get_redis_publisher),
                             redis_subscriber: Redis = Depends(get_redis_subscriber)):
    await websocket.accept()

    message_handler = MessageHandler(mongo_client, RedisStreamProducer(redis_publisher))
    await message_handler.getSavedMessage(websocket, room_id)

    redis_subscriber = RedisStreamSubscriber(redis_subscriber, websocket)
    await redis_subscriber.subscribe(room_id=room_id)

