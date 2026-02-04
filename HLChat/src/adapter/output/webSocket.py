from fastapi import WebSocket, Depends
from typing import Dict, List
import json

from redis.client import PubSub

from common.redis_pubsub import getRedis
from redis import Redis

class WebSocketConnectionManager:
    def __init__(self, redisSubscriber: Redis = Depends(getRedis)):
        # user_id를 key로, WebSocket을 value로 관리
        self.active_connections: Dict[str, WebSocket] = {}
        self.active_pubsubs: Dict[str, PubSub] = {}

    def store_connection(self, user_id: str, connection: WebSocket, redis_client: Redis):
        # 커넥션이 존재하면 닫은 후 새로 연결.
        if self.active_connections.get(user_id, None) is not None:
            old_connection: WebSocket = self.active_connections[user_id]
            old_pubsub = self.active_pubsubs[user_id]
            old_connection.close()
            old_pubsub.close()

        self.active_connections[user_id] = connection
        self.active_pubsubs[user_id] = redis_client.pubsub()


    async def disconnect(self, user_id: str, code:int | None = None, reason: str | None = None):
        """연결 해제 및 제거"""
        if user_id in self.active_connections:
            ws: WebSocket = self.active_connections[user_id]
            await ws.close(code, reason)
            del self.active_connections[user_id]
            print(f"사용자 {user_id} 연결 해제됨. 현재 접속자: {len(self.active_connections)}명")

    def is_connected(self, user_id: str) -> bool:
        """특정 사용자 연결 여부 확인"""
        return user_id in self.active_connections

    async def send_json(self, userId: str, data):
        await self.active_connections[userId].send_json(data)

    def get_connection(self, user_id: str) -> WebSocket:
        return self.active_connections.get(user_id, None)

    def get_pubsub(self, user_id: str) -> PubSub:
        return self.active_pubsubs.get(user_id, None)

manager = WebSocketConnectionManager()

def get_websocket_connection_manager():
    return manager
# 싱글톤 인스턴스
