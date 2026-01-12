from abc import ABC, abstractmethod
from typing import List, Dict

from domain.userRequest import AddTempUserRequest, ChangeUserPasswordRequest, LogInRequest, ChangeUsernameRequest
from domain.response import UserListSchema, UserSchema, JWTResponse


class SaveTempUserUsecase(ABC):
    @abstractmethod
    async def saveTempUser(self, request: AddTempUserRequest) -> UserSchema:
        pass

class ChangeUserPasswordUsecase(ABC):
    @abstractmethod
    async def changeUserPassword(self, request: ChangeUserPasswordRequest):
        pass

class FindUserUsecase(ABC):
    @abstractmethod
    async def findAllUsers(self) -> UserListSchema:
        pass

class FindUserByUserIdUsecase(ABC):
    @abstractmethod
    async def findUserByUserId(self, userId: str) -> UserSchema | None:
        pass

class LogInUsecase(ABC):
    @abstractmethod
    async def logIn(self, request: LogInRequest) -> JWTResponse:
        pass

class ChangeUsernameUsecase(ABC):
    @abstractmethod
    async def changeUsername(self, access_token: str, request: ChangeUsernameRequest) -> UserSchema:
        pass

class FindUserByRoomIdUsecase(ABC):
    @abstractmethod
    async def findUserByRoomId(self, roomId: int) -> Dict[str, str] | None:
        pass