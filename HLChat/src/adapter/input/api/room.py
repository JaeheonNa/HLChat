from fastapi import APIRouter, Depends

from application.port.input.roomUsecase import FindRoomIdUsecase, FindAllRoomsByUserIdUsecase
from application.service.roomService import FindRoomIdService, FindAllRoomsByUserIdService
from common.security import get_access_token

router = APIRouter(prefix="/room")

# @router.get("/{user_id}")
# async def findAllRoomsByUserId(
#         user_id: str,
#         access_token: str = Depends(get_access_token),
#         roomHandler: FindAllRoomsByUserIdUsecase = Depends(FindAllRoomsByUserIdService)
# ):
#     return await roomHandler.findAllRoomsByUserId(user_id)


@router.get("/{user_id}/{friend_id}")
async def findRoomIdByUserIdAndFriendId(
        user_id: str,
        friend_id: str,
        access_token: str = Depends(get_access_token),
        roomHandler: FindRoomIdUsecase = Depends(FindRoomIdService)
):
    return await roomHandler.findRoomIdByUserIdAndFriendId(user_id, friend_id)

