from abc import ABC, abstractmethod

from starlette.websockets import WebSocket

from domain.response import RoomListSchema
from domain.roomRequest import UpdateLastReadRequest


class FindRoomIdUsecase(ABC):
    @abstractmethod
    async def findRoomIdByUserIdAndFriendId(self, user_id: str, friend_id: str):
        pass

class FindAllRoomsByUserIdUsecase(ABC):
    @abstractmethod
    async def findAllRoomsByUserId(self, userId: str):
        pass

class FindAndSendAllRoomsLastMessagesUsecase(ABC):
    @abstractmethod
    async def findAndSendAllRoomsLastMessages(self, userId: str, roomList: RoomListSchema, websocket: WebSocket):
        pass

class UpdateLastReadUsecase(ABC):
    @abstractmethod
    async def updateLastRead(self, request: UpdateLastReadRequest, access_token: str):
        pass