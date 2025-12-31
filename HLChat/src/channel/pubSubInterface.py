from abc import ABC, abstractmethod

from starlette.websockets import WebSocket


class Producer(ABC):
    @abstractmethod
    def publish_message(self, room_id: str, message: dict) -> None:
        pass

class Subscriber(ABC):
    @abstractmethod
    async def subscribe_message(self, room_id: str, websocket: WebSocket) -> None:
        pass