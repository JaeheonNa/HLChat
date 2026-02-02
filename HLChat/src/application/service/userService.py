import os
import uuid
from typing import override, List, Dict

from fastapi import Depends, UploadFile
from fastapi import HTTPException

from adapter.output.roomPersistenceAdapter import RequestRoomPersistenceAdapter
from adapter.output.userPersistenceAdapter import RequestUserPersistenceAdapter
from application.port.input.userUsecase import (
    SaveTempUserUsecase, ChangeUserPasswordUsecase, FindUserUsecase,
    LogInUsecase, FindUserByUserIdUsecase, ChangeUsernameUsecase, FindUserByRoomIdUsecase,
    RegisterUsecase, GetMyProfileUsecase, UpdateMyProfileUsecase, UploadProfileImageUsecase
)
from application.port.output.roomPort import MongoRoomPort
from application.port.output.userPort import MariaUserPort
from common.mysql import getMySqlDB
from domain.response import UserSchema, UserListSchema, JWTResponse, MyProfileResponse, ProfileImageResponse
from domain.roomDomain import RoomDomain
from domain.userDomain import UserDomain
from domain.userRequest import (
    AddTempUserRequest, ChangeUserPasswordRequest, ChangeUsernameRequest,
    LogInRequest, RegisterRequest, UpdateMyProfileRequest
)


class SaveTempUserService(SaveTempUserUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def saveTempUser(self, request: AddTempUserRequest):
        user: UserDomain = await self.mariaUserPort.findUserByUserId(request.user_id)
        if user is None:
            userDomain: UserDomain = UserDomain.createTempUser(request)
            return await self.mariaUserPort.saveUser(userDomain)
        else:
            raise HTTPException(status_code=400, detail="Already exists userno")

class ChangeUserPasswordService(ChangeUserPasswordUsecase):
    def __init__(self,
               mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)
    ):
        self.mariaUserPort = mariaUserPort

    @override
    async def changeUserPassword(self, request: ChangeUserPasswordRequest):
        userDomain: UserDomain = await self.mariaUserPort.findUserByUserId(request.user_id)
        if userDomain is None:
            raise HTTPException(status_code=404, detail="User not found")

        verified: bool = userDomain.verifyPassword(request.password, userDomain.password)
        if verified:
            password = UserDomain.hashedPassword(request.new_password)
            userDomain.setPassword(password)
            inactive: bool = request.user_id == request.new_password
            userDomain.setActive(not inactive)
            if request.user_name is not None:
                userDomain.setUsername(request.user_name)
            await self.mariaUserPort.saveUser(userDomain)
        else:
            raise HTTPException(status_code=400, detail="Incorrect password")

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

class FindUserWithSocketService(FindUserByUserIdUsecase):

    @override
    async def findUserByUserId(self, userId: str) -> UserSchema | None:
        with getMySqlDB().getSessionFactory().begin() as session:
            self.mariaUserPort: MariaUserPort = RequestUserPersistenceAdapter(session)
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
                    password_expired = userDomain.isPasswordExpired()
                    accessToken = userDomain.createJWT()
                    return JWTResponse(
                        access_token=accessToken,
                        username=userDomain.username,
                        password_expired=password_expired
                    )
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

class FindUserByRoomIdService(FindUserByRoomIdUsecase):
    def __init__(self,
                 mongoRoomPort: MongoRoomPort = Depends(RequestRoomPersistenceAdapter),
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mongoRoomPort = mongoRoomPort
        self.mariaUserPort = mariaUserPort


    @override
    async def findUserByRoomId(self, room_id: int) -> Dict[str, str]:
        room: RoomDomain = await self.mongoRoomPort.findRoomByRoomId(room_id)
        members: List[str] = room.members
        users: List[UserDomain] = await self.mariaUserPort.findUsersByUserIds(members)
        usersDict = dict()
        for user in users:
            usersDict[user.userId] = user.username

        return usersDict


class RegisterService(RegisterUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mariaUserPort = mariaUserPort

    @override
    async def register(self, request: RegisterRequest) -> UserSchema:
        existing_user = await self.mariaUserPort.findUserByUserId(request.user_id)
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="이미 존재하는 사번입니다")

        userDomain = UserDomain.createUser(request)
        return await self.mariaUserPort.saveUser(userDomain)


class GetMyProfileService(GetMyProfileUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mariaUserPort = mariaUserPort

    @override
    async def getMyProfile(self, access_token: str) -> MyProfileResponse:
        user_id = UserDomain.decodeJWT(access_token)
        userDomain = await self.mariaUserPort.findUserByUserId(user_id)
        if userDomain is None:
            raise HTTPException(status_code=404, detail="User not found")

        return MyProfileResponse(
            user_id=userDomain.userId,
            user_name=userDomain.username,
            email=userDomain.email,
            phone=userDomain.phone,
            profile_image=userDomain.profile_image
        )


class UpdateMyProfileService(UpdateMyProfileUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mariaUserPort = mariaUserPort

    @override
    async def updateMyProfile(self, access_token: str, request: UpdateMyProfileRequest) -> MyProfileResponse:
        user_id = UserDomain.decodeJWT(access_token)
        userDomain = await self.mariaUserPort.findUserByUserId(user_id)
        if userDomain is None:
            raise HTTPException(status_code=404, detail="User not found")

        if request.user_name is not None:
            userDomain.setUsername(request.user_name)
        if request.email is not None:
            userDomain.setEmail(request.email)
        if request.phone is not None:
            userDomain.setPhone(request.phone)

        await self.mariaUserPort.saveUser(userDomain)

        return MyProfileResponse(
            user_id=userDomain.userId,
            user_name=userDomain.username,
            email=userDomain.email,
            phone=userDomain.phone,
            profile_image=userDomain.profile_image
        )


PROFILE_IMAGE_DIR = "static/profile_images"


class UploadProfileImageService(UploadProfileImageUsecase):
    def __init__(self,
                 mariaUserPort: MariaUserPort = Depends(RequestUserPersistenceAdapter)):
        self.mariaUserPort = mariaUserPort

    @override
    async def uploadProfileImage(self, access_token: str, file: UploadFile) -> ProfileImageResponse:
        user_id = UserDomain.decodeJWT(access_token)
        userDomain = await self.mariaUserPort.findUserByUserId(user_id)
        if userDomain is None:
            raise HTTPException(status_code=404, detail="User not found")

        os.makedirs(PROFILE_IMAGE_DIR, exist_ok=True)

        file_extension = file.filename.split(".")[-1] if file.filename else "png"
        unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(PROFILE_IMAGE_DIR, unique_filename)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        image_url = f"/static/profile_images/{unique_filename}"
        userDomain.setProfileImage(image_url)
        await self.mariaUserPort.saveUser(userDomain)

        return ProfileImageResponse(image_url=image_url)
