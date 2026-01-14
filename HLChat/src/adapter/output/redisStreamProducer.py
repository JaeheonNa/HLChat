import json
from typing import override

from fastapi import Depends
from redis import Redis

from application.port.output.messagePort import RedisPublishMessagePort
from common.redis_pubsub import getRedis

class RedisStreamProducer(RedisPublishMessagePort):
    def __init__(self, redisProducer: Redis = Depends(getRedis)):
        self.redisProducer = redisProducer

    @override
    async def publishMessage(self, roomId: str, message: dict):
        await self.redisProducer.publish(roomId, json.dumps(message))