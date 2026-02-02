from fastapi import APIRouter, Depends, UploadFile, File

from application.port.input.userUsecase import (
    SaveTempUserUsecase, ChangeUserPasswordUsecase, FindUserUsecase,
    LogInUsecase, ChangeUsernameUsecase, FindUserByRoomIdUsecase,
    RegisterUsecase, GetMyProfileUsecase, UpdateMyProfileUsecase, UploadProfileImageUsecase,
    VerifyTokenUsecase
)
from application.service.userService import (
    SaveTempUserService, ChangeUserPasswordService, FindUserService,
    LogInService, ChangeUsernameService, FindUserByRoomIdService,
    RegisterService, GetMyProfileService, UpdateMyProfileService, UploadProfileImageService,
    VerifyTokenService
)
from common.security import get_access_token
from domain.userRequest import (
    AddTempUserRequest, ChangeUserPasswordRequest, LogInRequest,
    ChangeUsernameRequest, RegisterRequest, UpdateMyProfileRequest
)

router = APIRouter(prefix="/user")


@router.post("/temp", status_code=201)
async def saveTempUser(
    request: AddTempUserRequest,
    userHandler: SaveTempUserUsecase = Depends(SaveTempUserService)
):
    return await userHandler.saveTempUser(request)


@router.put("/temp", status_code=202)
async def changePassword(
    request: ChangeUserPasswordRequest,
    userHandler: ChangeUserPasswordUsecase = Depends(ChangeUserPasswordService)
):
    await userHandler.changeUserPassword(request)


@router.post("/register", status_code=201)
async def register(
    request: RegisterRequest,
    userHandler: RegisterUsecase = Depends(RegisterService)
):
    return await userHandler.register(request)


@router.get("/me", status_code=200)
async def getMyProfile(
    access_token: str = Depends(get_access_token),
    userHandler: GetMyProfileUsecase = Depends(GetMyProfileService)
):
    return await userHandler.getMyProfile(access_token)


@router.put("/me", status_code=200)
async def updateMyProfile(
    request: UpdateMyProfileRequest,
    access_token: str = Depends(get_access_token),
    userHandler: UpdateMyProfileUsecase = Depends(UpdateMyProfileService)
):
    return await userHandler.updateMyProfile(access_token, request)


@router.post("/profile-image", status_code=200)
async def uploadProfileImage(
    image: UploadFile = File(...),
    access_token: str = Depends(get_access_token),
    userHandler: UploadProfileImageUsecase = Depends(UploadProfileImageService)
):
    return await userHandler.uploadProfileImage(access_token, image)


@router.put("/username", status_code=202)
async def changeUsername(
    request: ChangeUsernameRequest,
    access_token: str = Depends(get_access_token),
    userHandler: ChangeUsernameUsecase = Depends(ChangeUsernameService)
):
    return await userHandler.changeUsername(access_token, request)


@router.get("", status_code=200)
async def findAllUsers(
    access_token=Depends(get_access_token),
    userHandler: FindUserUsecase = Depends(FindUserService)
):
    return await userHandler.findAllUsers()


@router.post("/log-in", status_code=200)
async def logIn(
    request: LogInRequest,
    userHandler: LogInUsecase = Depends(LogInService)
):
    return await userHandler.logIn(request)


@router.get("/{room_id}", status_code=200)
async def findUserByRoomId(
    room_id: int,
    userHandler: FindUserByRoomIdUsecase = Depends(FindUserByRoomIdService)
):
    print("room_id: ", room_id)
    return await userHandler.findUserByRoomId(room_id)