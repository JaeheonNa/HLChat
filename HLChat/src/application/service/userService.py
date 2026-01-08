from typing import override, List

from fastapi import Depends

from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.input.userUsecase import SaveTempUserUsecase, ChangeUserPasswordUsecase, FindUserUsecase, \
    LogInUsecase, FindUserByUserIdUsecase, ChangeUsernameUsecase
from application.port.output.userPort import MariaUserPort
from config import secret_key, jwt_algorithm
from domain.userDomain import UserDomain
from domain.userRequest import AddTempUserRequest, ChangeUserPasswordRequest, ChangeUsernameRequest
from domain.orm import User
from domain.response import UserSchema, UserListSchema, JWTResponse
from domain.userRequest import LogInRequest
from fastapi import HTTPException
from jose import jwt


class SaveTempUserService(SaveTempUserUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def saveTempUser(self, request: AddTempUserRequest):
        userDomain: UserDomain = UserDomain.createTempUser(request)
        return await self.mariaUserPort.saveUser(userDomain)

class ChangeUserPasswordService(ChangeUserPasswordUsecase):
    def __init__(self,
               mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def changeUserPassword(self, request: ChangeUserPasswordRequest):
        userDomain: UserDomain = await self.mariaUserPort.findUserByUserId(request.user_id)

        verified: bool = userDomain.verifyPassword(request.password, userDomain.password)
        if verified:
            password = UserDomain.hashedPassword(request.new_password)
            userDomain.setPassword(password)
            inactive: bool = request.user_id is request.new_password
            userDomain.setActive(not inactive)
            await self.mariaUserPort.saveUser(userDomain)

class FindUserService(FindUserUsecase, FindUserByUserIdUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def findAllUsers(self) -> UserListSchema:
        return UserListSchema(
            users=await self.mariaUserPort.findAllUsers()
        )

    @override
    async def findUserByUserId(self, userId: str) -> UserSchema | None:
        userDomain: UserDomain = await self.mariaUserPort.findUserByUserId(userId)
        if userDomain:
            return UserSchema(userId=userDomain.userId, username=userDomain.username, active=userDomain.active)
        return None

class LogInService(LogInUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def logIn(self, request: LogInRequest) -> JWTResponse:
        userDomain: UserDomain = await self.mariaUserPort.findUserByUserId(request.user_id)
        if userDomain:
            if userDomain.active:
                verified: bool = UserDomain.verifyPassword(request.password, userDomain.password)
                if verified:
                    accessToken = userDomain.createJWT()
                    return JWTResponse(access_token=accessToken, username=userDomain.username)
                else:
                    raise HTTPException(status_code=401, detail="Not Authorized")
            else:
                raise HTTPException(status_code=403, detail="Inactive user. Password changing is required.")
        else:
            raise HTTPException(status_code=404, detail="User not found")

class ChangeUsernameService(ChangeUsernameUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mariaUserPort = mariaUserPort

    @override
    async def changeUsername(self, access_token: str, request: ChangeUsernameRequest) -> UserSchema:
        user_id: str = UserDomain.decodeJWT(access_token)
        userDomain: UserDomain = await self.mariaUserPort.findUserByUserId(user_id)
        userDomain.setUsername(request.username)
        return await self.mariaUserPort.saveUser(userDomain)