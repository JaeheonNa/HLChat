from typing import override

from fastapi import Depends
from redis import Redis
from starlette.websockets import WebSocket

from application.port.output.messagePort import RedisSubscribeMessagePort
from common.redis_pubsub import getRedisSubscriber


class RedisStreamSubscriber(RedisSubscribeMessagePort):
    def __init__(self, redisSubscriber: Redis = Depends(getRedisSubscriber)):
        self.redisSubscriber = redisSubscriber
        self.pubSub = redisSubscriber.pubsub()

    @override
    async def subscribeMessage(self, room_id: str, websocket: WebSocket):
        await self.pubSub.subscribe(room_id)

        async for message in self.pubSub.listen():
            if message['type'] == 'message':
                data = message['data']
                if not isinstance(data, str):
                    data = str(data)
                await websocket.send_text(data)