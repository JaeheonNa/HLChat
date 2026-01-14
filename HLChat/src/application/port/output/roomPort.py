from abc import ABC, abstractmethod

from domain.messageRequest import SendMessageRequest
from domain.response import RoomListSchema, RoomSchema
from domain.roomDomain import RoomDomain
from domain.roomRequest import SaveRoomRequest, UpdateLastReadRequest


class MongoRoomPort(ABC):
    @abstractmethod
    async def findRoomId(self) -> int:
        pass

    @abstractmethod
    async def createRoom(self, request: SaveRoomRequest) -> int:
        pass

    @abstractmethod
    async def findRoomIdByUserIdAndFriendId(self, user_id: str, friend_id: str) -> int | None:
        pass

    @abstractmethod
    async def findRoomByRoomId(self, room_id: int) -> RoomDomain:
        pass

    @abstractmethod
    async def updateRoomLastInfo(self, request: SendMessageRequest, newMessageLnNo: int) -> RoomSchema | None:
        pass

    @abstractmethod
    async def findAllRoomsByUserId(self, userId: str) -> RoomListSchema:
        pass

    @abstractmethod
    async def updateLastRead(self, request: UpdateLastReadRequest, userId: str):
        pass