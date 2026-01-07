import json
from typing import override

from fastapi import Depends
from redis import Redis

from application.port.output.messagePort import RedisPublishMessagePort
from common.redis_pubsub import getRedisProducer

class RedisStreamProducer(RedisPublishMessagePort):
    def __init__(self, redisProducer: Redis = Depends(getRedisProducer)):
        self.redisProducer = redisProducer

    @override
    def publishMessage(self, room_id: str, message: dict):
        self.redisProducer.publish(room_id, json.dumps(message))