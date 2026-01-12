from abc import ABC, abstractmethod
from typing import Any, List

from starlette.websockets import WebSocket

from domain.messageRequest import SendMessageRequest
from domain.odm import HLChatMessage


class MongoMessagePort(ABC):
    @abstractmethod
    async def saveMessage(self, request: SendMessageRequest):
        pass

    @abstractmethod
    async def findSavedMessage(self, room_id: int) -> List[HLChatMessage] | None:
        pass


class RedisPublishMessagePort(ABC):
    @abstractmethod
    def publishMessage(self, room_id: str, message: dict):
        pass

class RedisSubscribeMessagePort(ABC):
    @abstractmethod
    async def subscribeMessage(self, room_id: str, websocket: WebSocket):
        pass