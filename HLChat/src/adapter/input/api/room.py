from fastapi import APIRouter, Depends

from application.port.input.roomUsecase import FindRoomIdUsecase, UpdateLastReadUsecase, CreateGroupRoomUsecase, \
    UpdateRoomMemberUseCase, FindRoomInfoByRoomIdUseCase, InviteMembersUsecase
from application.service.roomService import FindRoomIdService, UpdateLastReadService, CreateGroupRoomService, \
    UpdateRoomMemberService, FindRoomInfoByRoomIdService, InviteMembersService
from common.security import get_access_token
from domain.response import UserListSchema
from domain.roomRequest import UpdateLastReadRequest, CreateGroupRoomRequest, InviteMembersRequest
from domain.userDomain import UserDomain

router = APIRouter(prefix="/room")

@router.get("")
async def findRoomIdByUserIdAndFriendId(
        user_id: str,  # query parameter로 직접 받기
        friend_id: str,  # query parameter로 직접 받기
        access_token: str = Depends(get_access_token),
        roomHandler: FindRoomIdUsecase = Depends(FindRoomIdService)
):
    return await roomHandler.findRoomIdByUserIdAndFriendId(user_id, friend_id)

@router.put("/last-read")
async def updateLastRead(request: UpdateLastReadRequest,
                         access_token: str = Depends(get_access_token),
                         roomHandler: UpdateLastReadUsecase = Depends(UpdateLastReadService)
                         ):
    await roomHandler.updateLastRead(request, access_token)

@router.post("/group")
async def createGroupRoom(
    request: CreateGroupRoomRequest,
    access_token: str = Depends(get_access_token),
    roomHandler: CreateGroupRoomUsecase = Depends(CreateGroupRoomService)
):
    return await roomHandler.createGroupRoom(request, access_token)

@router.post("/{room_id}/leave")
async def leaveRoom(
        room_id: int,
        access_token: str = Depends(get_access_token),
        roomHandler: UpdateRoomMemberUseCase = Depends(UpdateRoomMemberService)
):
    userId: str = UserDomain.decodeJWT(access_token)
    await roomHandler.leaveRoom(room_id, userId)

@router.get("/{room_id}/info")
async def findRoomInfoByRoomId(
        room_id: int,
        access_token: str = Depends(get_access_token),
        roomHandler: FindRoomInfoByRoomIdUseCase = Depends(FindRoomInfoByRoomIdService)
):
    userId: str = UserDomain.decodeJWT(access_token)
    return await roomHandler.findRoomInfoByRoomId(room_id, userId)

@router.post("/{room_id}/invitation")
async def inviteMembers(
        room_id: int,
        request: InviteMembersRequest,
        access_token: str = Depends(get_access_token),
        roomHandler: InviteMembersUsecase = Depends(InviteMembersService)
):
    user_id: str = UserDomain.decodeJWT(access_token)
    invitedUserList: UserListSchema = await roomHandler.inviteMembers(room_id, user_id, request)
    return invitedUserList