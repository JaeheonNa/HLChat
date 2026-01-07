from fastapi import APIRouter, Depends

from application.port.input.userUsecase import SaveTempUserUsecase, ChangeUserPasswordUsecase, FindUserUsecase, \
    LogInUsecase
from application.service.userService import SaveTempUserService, ChangeUserPasswordService, FindUserService, \
    LogInService
from domain.userRequest import AddTempUserRequest, ChangeUserPasswordRequest, LogInRequest

router = APIRouter(prefix="/user")

@router.post("/temp", status_code=201)
async def saveTempUser(
    request: AddTempUserRequest,
    userHandler: SaveTempUserUsecase = Depends(SaveTempUserService)
):
    return await userHandler.saveTempUser(request)

@router.put("/temp", status_code=202)
async def changePassword(request: ChangeUserPasswordRequest,
                         userHandler: ChangeUserPasswordUsecase = Depends(ChangeUserPasswordService)
):
    await userHandler.changeUserPassword(request)

@router.get("", status_code=200)
async def findAllUsers(userHandler: FindUserUsecase = Depends(FindUserService)):
    return await userHandler.findAllUsers()

@router.post("/log-in", status_code=200)
async def logIn(request: LogInRequest,
                userHandler: LogInUsecase = Depends(LogInService)
):
    return await userHandler.logIn(request)