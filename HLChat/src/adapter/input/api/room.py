from fastapi import APIRouter, Depends

from application.port.input.roomUsecase import FindRoomIdUsecase
from application.service.roomService import FindRoomIdService

router = APIRouter(prefix="/room")

@router.get("/{user_id}/{friend_id}")
async def findAllRooms(
        user_id: str,
        friend_id: str,
        roomHandler: FindRoomIdUsecase = Depends(FindRoomIdService)
):
    return await roomHandler.findRoomIdByUserIdAndFriendId(user_id, friend_id)