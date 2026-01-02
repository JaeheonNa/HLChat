import json

from fastapi import Depends
from redis import Redis
from starlette.websockets import WebSocket
from typing_extensions import override

from channel.channel import get_redis_producer, get_redis_subscriber
from channel.pubSubInterface import Producer, Subscriber


class RedisStreamProducer(Producer):
    def __init__(self, redis_producer: Redis = Depends(get_redis_producer)):
        self.redis_producer = redis_producer

    @override
    def publish_message(self, room_id: str, message: dict):
        self.redis_producer.publish(room_id, json.dumps(message))

class RedisStreamSubscriber(Subscriber):
    def __init__(self, redis_subscriber: Redis = Depends(get_redis_subscriber)):
        self.redis_subscriber = redis_subscriber
        self.pub_sub = redis_subscriber.pubsub()

    @override
    async def subscribe_message(self, room_id: str, websocket: WebSocket):
        await self.pub_sub.subscribe(room_id)

        async for message in self.pub_sub.listen():
            if message['type'] == 'message':
                data = message['data']
                if not isinstance(data, str):
                    data = str(data)
                await websocket.send_text(data)