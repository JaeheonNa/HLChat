from abc import ABC, abstractmethod

from domain.userRequest import AddTempUserRequest, ChangeUserPasswordRequest, LogInRequest
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

class LogInUsecase(ABC):
    @abstractmethod
    async def logIn(self, request: LogInRequest) -> JWTResponse:
        pass
