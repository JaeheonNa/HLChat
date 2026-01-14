from fastapi import APIRouter, Depends

from application.port.input.roomUsecase import FindRoomIdUsecase, UpdateLastReadUsecase
from application.service.roomService import FindRoomIdService, UpdateLastReadService
from common.security import get_access_token
from domain.roomRequest import UpdateLastReadRequest

router = APIRouter(prefix="/room")

@router.get("/{user_id}/{friend_id}")
async def findRoomIdByUserIdAndFriendId(
        user_id: str,
        friend_id: str,
        access_token: str = Depends(get_access_token),
        roomHandler: FindRoomIdUsecase = Depends(FindRoomIdService)
):
    return await roomHandler.findRoomIdByUserIdAndFriendId(user_id, friend_id)

@router.put("/last-read")
async def updateLastRead(request: UpdateLastReadRequest,
                         access_token: str = Depends(get_access_token),
                         roomHandler: UpdateLastReadUsecase = Depends(UpdateLastReadService)
                         ):
    print("updateLastRead")
    await roomHandler.updateLastRead(request, access_token)