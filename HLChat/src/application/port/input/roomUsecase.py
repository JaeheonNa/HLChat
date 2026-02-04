from abc import ABC, abstractmethod

from starlette.websockets import WebSocket

from domain.response import RoomListSchema, UserListSchema
from domain.roomRequest import UpdateLastReadRequest, CreateGroupRoomRequest, InviteMembersRequest


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
    async def findAndSendAllRoomsLastMessages(self, userId: str, roomList: RoomListSchema):
        pass

class UpdateLastReadUsecase(ABC):
    @abstractmethod
    async def updateLastRead(self, request: UpdateLastReadRequest, access_token: str):
        pass

class CreateGroupRoomUsecase(ABC):
    @abstractmethod
    async def createGroupRoom(self, request: CreateGroupRoomRequest, access_token: str):
        pass

class UpdateRoomMemberUseCase(ABC):
    @abstractmethod
    async def leaveRoom(self, roomId: int, userId: str):
        pass

    @abstractmethod
    async def addRoomMember(self, roomId: int, userId: str, memberId: str):
        pass

class FindRoomInfoByRoomIdUseCase(ABC):
    @abstractmethod
    async def findRoomInfoByRoomId(self, roomId: int, userId: str):
        pass

class InviteMembersUsecase(ABC):
    @abstractmethod
    async def inviteMembers(self, roomId: int, userId: str, request: InviteMembersRequest) -> UserListSchema:
        pass