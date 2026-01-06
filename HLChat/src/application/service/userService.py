from typing import override

from fastapi import Depends

from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.input.userUsecase import SaveTempUserUsecase, ChangeUserPasswordUsecase, FindUserUsecase, \
    LogInUsecase
from application.port.output.userPort import MariaUserPort
from domain.userRequest import AddTempUserRequest, ChangeUserPasswordRequest
from domain.orm import User
from domain.response import UserSchema, UserListSchema, JWTResponse
from domain.userRequest import LogInRequest
from fastapi import HTTPException


class SaveTempUserService(SaveTempUserUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def saveTempUser(self, request: AddTempUserRequest):
        user = User.createTempUser(request)
        user = await self.mariaUserPort.saveUser(user)
        return UserSchema.model_validate(user)



class ChangeUserPasswordService(ChangeUserPasswordUsecase):
    def __init(self,
               mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def changeUserPassword(self, request: ChangeUserPasswordRequest):
        user = await self.mariaUserPort.findUserByUserId(request.user_id)
        verified: bool = user.verifyPassword(request.password, user.password)
        if verified:
            user.password = User.hashedPassword(request.new_password)
            inactive: bool = user.verifyPassword(request.user_id, request.new_password)
            user.active = not inactive
            await self.mariaUserPort.saveUser(user)



class FindUserService(FindUserUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def findAllUsers(self) -> UserListSchema:
        users = await self.mariaUserPort.findAllUsers()
        return UserListSchema(
            users=[UserSchema.model_validate(user) for user in users]
        )



class LogInService(LogInUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def logIn(self, request: LogInRequest) -> JWTResponse:
        user = await self.mariaUserPort.findUserByUserId(request.user_id)
        if user:
            if user.active:
                verified: bool = User.verifyPassword(request.password, user.password)
                if verified:
                    accessToken = user.createJwt()
                    return JWTResponse(access_token=accessToken)
                else:
                    raise HTTPException(status_code=401, detail="Not Authorized")
            else:
                raise HTTPException(status_code=403, detail="Inactive user. Password changing is required.")
        else:
            raise HTTPException(status_code=404, detail="User not found")