from abc import ABC, abstractmethod
from typing import Any, List

from starlette.websockets import WebSocket

from domain.messageRequest import SendMessageRequest
from domain.odm import HLChatMessage
from domain.response import RoomListSchema


class MongoMessagePort(ABC):
    @abstractmethod
    async def saveMessage(self, request: SendMessageRequest) -> int:
        pass

    @abstractmethod
    async def findSavedMessage(self, room_id: int, message_ln_no: int | None = None) -> List[HLChatMessage] | None:
        pass


class RedisPublishMessagePort(ABC):
    @abstractmethod
    def publishMessage(self, room_id: str, message: dict):
        pass

class RedisSubscribeMessagePort(ABC):
    @abstractmethod
    async def subscribeMessage(self, roomList: RoomListSchema, websocket: WebSocket, userId: str):
        pass