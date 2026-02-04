from abc import ABC, abstractmethod

from starlette.websockets import WebSocket


class FindCurrentWebSocketsUsecase(ABC):
    @abstractmethod
    async def findCurrentWebSockets(self):
        pass
