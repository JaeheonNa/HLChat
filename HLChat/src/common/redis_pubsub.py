import redis
from redis import asyncio as aioredis
from config import redis_host, redis_port, redis_db

redisProducer = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
redisSubscriber = aioredis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

def getRedisProducer():
    return redisProducer

def getRedisSubscriber():
    return redisSubscriber