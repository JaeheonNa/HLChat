from redis import asyncio as aioredis
from config import redis_host, redis_port, redis_db

redis = aioredis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

def getRedis():
    return redis