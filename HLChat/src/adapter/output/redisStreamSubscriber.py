import asyncio
import json
from typing import override, Dict

from fastapi import Depends
from starlette.websockets import WebSocket

from application.port.output.messagePort import RedisSubscribeMessagePort
from common.redisPubSubManager import RedisPubSubManager, get_connection_manager
from adapter.output.webSocket import WebSocketConnectionManager, get_websocket_connection_manager
from domain.response import RoomListSchema


class RedisStreamSubscriber(RedisSubscribeMessagePort):
    def __init__(self,
                 redisPubSubManager: RedisPubSubManager = Depends(get_connection_manager),
                 connectionManager: WebSocketConnectionManager = Depends(get_websocket_connection_manager)):
        self.redisPubSubManager = redisPubSubManager
        self.connectionManager = connectionManager

    async def unsubscribe_from_room(self, room_id:str, user_id: str):
        if room_id in self.redisPubSubManager.subscribed_rooms.get(user_id, set()):
            await self.connectionManager.get_pubsub(user_id).unsubscribe(room_id)
            self.redisPubSubManager.subscribed_rooms.get(user_id).remove(room_id)

    async def subscribe_to_room(self, user_id:str, room_id: str):
        if room_id not in self.redisPubSubManager.subscribed_rooms.get(user_id, set()):
            await self.connectionManager.get_pubsub(user_id).subscribe(room_id)
            self.redisPubSubManager.subscribed_rooms.get(user_id, set()).add(room_id)

    # 초대하기를 통해 구독할 때 사용되는 메서드.
    @override
    async def subscribeXRoomMessage(self, roomId: int, userId: str):
        websocket: WebSocket | None = self.connectionManager.get_connection(userId)
        if websocket is None:
            print(userId, "is not Active.")
            return
        self.redisPubSubManager.connect(userId, self)
        await self.redisPubSubManager.add_room_subscription(userId, str(roomId))

    @override
    async def subscribeMessage(self, roomList: RoomListSchema, userId: str):
        websocket: WebSocket | None = self.connectionManager.get_connection(userId)
        if websocket is None:
            return
        self.redisPubSubManager.connect(userId, self)
        channels = [str(room.roomId) for room in roomList.rooms]
        for channel in channels:
            await self.redisPubSubManager.add_room_subscription(userId, channel)

        if not channels:
            print("구독할 방이 없습니다. 대기 모드로 전환합니다.")
            while len(self.redisPubSubManager.subscribed_rooms.get(userId, set())) == 0:
                print("대기 중")
                await asyncio.sleep(5)  # 소켓이 끊기지 않도록 무한 대기
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    print("연결 끊김 감지 (ping 실패)")
                    break

        async for message in self.connectionManager.get_pubsub(userId).listen():
            if message['type'] == 'message':
                # channel: bytes → str 변환
                roomId = message['channel']
                # data: bytes → str → dict 변환
                messageData = json.loads(message['data'])

                # 반응 메시지는 별도 처리
                if messageData.get("type") == "reaction":
                    await websocket.send_json({
                        'type': 'reaction',
                        'roomId': roomId,
                        'messageLnNo': messageData.get("messageLnNo"),
                        'reactionType': messageData.get("reactionType"),
                        'userId': messageData.get("userId"),
                        'userName': messageData.get("userName"),
                        'action': messageData.get("action"),
                        'reactions': messageData.get("reactions")
                    })
                    continue

                lastRead: Dict[str, int] = messageData.get("lastRead", 0)
                lastUpdateMessageLnNo: int = messageData.get("lastUpdateMessageLnNo", 0)
                unreadMsgCnt = lastUpdateMessageLnNo - lastRead.get(userId, 0)
                messageData.update({'unreadMessageCount': unreadMsgCnt})
                await websocket.send_json({
                    'roomId': roomId,
                    'messageData': messageData  # {"sender_id": "...", "message": "...", ...}
                })

        self.redisPubSubManager.disconnect(userId)