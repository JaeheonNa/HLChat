from abc import ABC, abstractmethod

from domain.messageRequest import SendMessageRequest


class MongoRoomPort(ABC):
    @abstractmethod
    async def save_room(self, request: SendMessageRequest) -> int:
        pass
