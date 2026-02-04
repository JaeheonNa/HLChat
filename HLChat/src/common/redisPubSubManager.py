from typing import Dict
from starlette.websockets import WebSocket


class RedisPubSubManager:
    def __init__(self):
        self.active_subscribers: Dict[str, 'RedisStreamSubscriber'] = {}
        self.subscribed_rooms: Dict[str, set()] = {}

    def connect(self, user_id: str, subscriber: 'RedisStreamSubscriber'):
        """새 연결 등록"""
        self.active_subscribers[user_id] = subscriber

    def disconnect(self, user_id: str):
        """연결 해제"""
        if user_id in self.active_subscribers:
            del self.active_subscribers[user_id]
        print(f"User {user_id} disconnected. Total: {len(self.active_subscribers)}")

    async def add_room_subscription(self, user_id: str, room_id: str):
        subscriber = self.active_subscribers.get(user_id)
        if subscriber:
            await subscriber.subscribe_to_room(user_id, room_id)
        else:
            print(f"User {user_id} not connected - will subscribe on next login")

    def get_subscriber(self, user_id: str):
        """사용자의 subscriber 조회"""
        return self.active_subscribers.get(user_id)


# 싱글톤 인스턴스
redisPubSubManager = RedisPubSubManager()


def get_connection_manager():
    return redisPubSubManager