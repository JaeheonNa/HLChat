import redis
from redis import asyncio as aioredis

redis_producer = redis.Redis(host="127.0.0.1", port=6380, db=0, decode_responses=True)
redis_subscriber = aioredis.Redis(host="127.0.0.1", port=6380, db=0, decode_responses=True)

def get_redis_producer():
    return redis_producer

def get_redis_subscriber():
    return redis_subscriber