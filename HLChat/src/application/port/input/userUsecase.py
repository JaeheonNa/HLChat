from abc import ABC, abstractmethod
from typing import Dict

from fastapi import UploadFile

from domain.userRequest import (
    AddTempUserRequest, ChangeUserPasswordRequest, LogInRequest,
    ChangeUsernameRequest, RegisterRequest, UpdateMyProfileRequest
)
from domain.response import UserListSchema, UserSchema, JWTResponse, MyProfileResponse, ProfileImageResponse


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


class RegisterUsecase(ABC):
    @abstractmethod
    async def register(self, request: RegisterRequest) -> UserSchema:
        pass


class GetMyProfileUsecase(ABC):
    @abstractmethod
    async def getMyProfile(self, access_token: str) -> MyProfileResponse:
        pass


class UpdateMyProfileUsecase(ABC):
    @abstractmethod
    async def updateMyProfile(self, access_token: str, request: UpdateMyProfileRequest) -> MyProfileResponse:
        pass


class UploadProfileImageUsecase(ABC):
    @abstractmethod
    async def uploadProfileImage(self, access_token: str, file: UploadFile) -> ProfileImageResponse:
        pass


class VerifyTokenUsecase(ABC):
    @abstractmethod
    async def verifyToken(self, access_token: str) -> MyProfileResponse:
        pass