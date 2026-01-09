from abc import ABC, abstractmethod

from starlette.websockets import WebSocket

from domain.messageRequest import SendMessageRequest

class SaveAndSendMessageUsecase(ABC):
    @abstractmethod
    async def saveAndSendMessage(self, request: SendMessageRequest) -> None:
        pass


class FindSavedMessageUsecase(ABC):

    @abstractmethod
    async def findSavedMessage(self, room_id: int, websocket: WebSocket) -> None:
        pass

class SubscribeMessageUsecase(ABC):
    @abstractmethod
    async def subscribeMessage(self, room_id: int, websocket: WebSocket) -> None:
        pass



