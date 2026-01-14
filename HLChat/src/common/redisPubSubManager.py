from typing import Dict
from starlette.websockets import WebSocket


class RedisPubSubManager:
    def __init__(self):
        # user_id -> subscriber 매핑
        self.active_subscribers: Dict[str, 'RedisStreamSubscriber'] = {}
        # user_id -> websocket 매핑
        self.active_connections: Dict[str, WebSocket] = {}

    def connect(self, user_id: str, subscriber: 'RedisStreamSubscriber', websocket: WebSocket):
        """새 연결 등록"""
        self.active_subscribers[user_id] = subscriber
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected. Total: {len(self.active_subscribers)}")

    def disconnect(self, user_id: str):
        """연결 해제"""
        if user_id in self.active_subscribers:
            del self.active_subscribers[user_id]
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        print(f"User {user_id} disconnected. Total: {len(self.active_subscribers)}")

    async def add_room_subscription(self, user_id: str, room_id: str):
        """특정 사용자에게 새 채팅방 구독 추가"""
        subscriber = self.active_subscribers.get(user_id)
        if subscriber:
            await subscriber.subscribe_to_room(room_id)
            print(f"Added room {room_id} subscription to user {user_id}")
        else:
            print(f"User {user_id} not connected - will subscribe on next login")

    def get_subscriber(self, user_id: str):
        """사용자의 subscriber 조회"""
        return self.active_subscribers.get(user_id)


# 싱글톤 인스턴스
redisPubSubManager = RedisPubSubManager()


def get_connection_manager():
    return redisPubSubManager