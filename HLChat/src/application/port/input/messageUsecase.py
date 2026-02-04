from abc import ABC, abstractmethod
from typing import List

from starlette.websockets import WebSocket

from domain.messageRequest import SendMessageRequest
from domain.response import RoomListSchema


class SaveAndSendMessageUsecase(ABC):
    @abstractmethod
    async def saveAndSendMessage(self, request: SendMessageRequest) -> None:
        pass

class SubscribeMessageUsecase(ABC):
    @abstractmethod
    async def subscribeMessage(self, roomList: RoomListSchema, userId: str) -> None:
        pass

class FindSavedMessageUsecase(ABC):
    @abstractmethod
    async def findSavedMessagesByRoomId(self, room_id: int, message_ln_no: int | None = None) -> None:
        pass



