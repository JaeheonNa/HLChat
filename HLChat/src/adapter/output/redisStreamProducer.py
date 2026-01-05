import json
from typing import override

from fastapi import Depends
from redis import Redis

from application.port.output.messagePort import RedisPublishMessagePort
from common.redis_pubsub import getRedisProducer

class RedisStreamProducer(RedisPublishMessagePort):
    def __init__(self, redis_producer: Redis = Depends(getRedisProducer)):
        self.redis_producer = redis_producer

    @override
    def publishMessage(self, room_id: str, message: dict):
        self.redis_producer.publish(room_id, json.dumps(message))