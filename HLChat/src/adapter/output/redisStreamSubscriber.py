import asyncio
import json
from typing import override, Dict

from fastapi import Depends
from redis import Redis
from starlette.websockets import WebSocket

from application.port.output.messagePort import RedisSubscribeMessagePort
from common.redisPubSubManager import RedisPubSubManager, get_connection_manager
from common.redis_pubsub import getRedis
from domain.response import RoomListSchema


class RedisStreamSubscriber(RedisSubscribeMessagePort):
    def __init__(self,
                 redisPubSubManager: RedisPubSubManager = Depends(get_connection_manager),
                 redisSubscriber: Redis = Depends(getRedis)):
        self.redisSubscriber = redisSubscriber # ← 공유된 Redis 연결
        self.pubSub = redisSubscriber.pubsub() # ← 각자 별도의 pubsub 객체!
        self.subscribed_rooms: set = set()
        self.redisPubSubManager = redisPubSubManager

    async def subscribe_to_room(self, room_id: str):
        """동적으로 새 채팅방 구독"""
        if room_id not in self.subscribed_rooms:
            await self.pubSub.subscribe(room_id)
            self.subscribed_rooms.add(room_id)
            print(f"Dynamically subscribed to room: {room_id}")

    @override
    async def subscribeMessage(self, roomList: RoomListSchema, websocket: WebSocket, userId: str):
        self.redisPubSubManager.connect(userId, self, websocket)
        channels = [str(room) for room in roomList.rooms]
        for channel in channels:
            await self.redisPubSubManager.add_room_subscription(userId, channel)

        if not channels:
            print("구독할 방이 없습니다. 대기 모드로 전환합니다.")
            while len(self.subscribed_rooms) == 0:
                print(userId, "'s, subscribed rooms:", self.subscribed_rooms)
                await asyncio.sleep(3)  # 소켓이 끊기지 않도록 무한 대기

        print("pubsub subscribed")
        async for message in self.pubSub.listen():
            if message['type'] == 'message':
                # channel: bytes → str 변환
                roomId = message['channel']
                # data: bytes → str → dict 변환
                messageData = json.loads(message['data'])
                lastRead: Dict[str, int] = messageData.get("lastRead", 0)
                lastUpdateMessageLnNo: int = messageData.get("lastUpdateMessageLnNo", 0)
                unreadMsgCnt = lastUpdateMessageLnNo - lastRead.get(userId)
                messageData.update({'unreadMessageCount': unreadMsgCnt})
                await websocket.send_json({
                    'roomId': roomId,
                    'messageData': messageData  # {"sender_id": "...", "message": "...", ...}
                })

        self.redisPubSubManager.disconnect(userId)