from fastapi import APIRouter, Depends

router = APIRouter(prefix="/room")

@router.get("/{user_id}")
async def findAllRooms():
    pass

