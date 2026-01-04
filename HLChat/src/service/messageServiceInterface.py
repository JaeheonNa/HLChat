from abc import ABC, abstractmethod

from starlette.websockets import WebSocket

from schema.request import SendMessageRequest


class MessageHandlerInterface(ABC):
    @abstractmethod
    def handleMessage(self, request: SendMessageRequest) -> None:
        pass

    @abstractmethod
    async def getSavedMessage(self, room_id: str, websocket: WebSocket) -> None:
        pass

    @abstractmethod
    async def subscribe_message(self, room_id: str, websocket: WebSocket) -> None:
        pass