from fastapi import APIRouter, Depends

from application.port.input.reactionUsecase import (
    ToggleReactionUsecase,
    FindReactionsByMessageUsecase,
    FindReactionsByRoomUsecase
)
from application.service.reactionService import (
    ToggleReactionService,
    FindReactionsByMessageService,
    FindReactionsByRoomService
)
from common.security import get_access_token
from domain.reactionRequest import ToggleReactionRequest

router = APIRouter(prefix="/hl-chat/reaction")


@router.post("", status_code=200)
async def toggle_reaction(
    request: ToggleReactionRequest,
    access_token=Depends(get_access_token),
    toggle_reaction_usecase: ToggleReactionUsecase = Depends(ToggleReactionService)
):
    """반응 토글 (추가/제거)"""
    return await toggle_reaction_usecase.toggleReaction(request)


@router.get("/{room_id}/{message_ln_no}")
async def get_message_reactions(
    room_id: int,
    message_ln_no: int,
    access_token=Depends(get_access_token),
    find_reactions_usecase: FindReactionsByMessageUsecase = Depends(FindReactionsByMessageService)
):
    """특정 메시지의 반응 조회"""
    return await find_reactions_usecase.findReactionsByMessage(room_id, message_ln_no)


@router.get("/{room_id}")
async def get_room_reactions(
    room_id: int,
    access_token=Depends(get_access_token),
    find_reactions_usecase: FindReactionsByRoomUsecase = Depends(FindReactionsByRoomService)
):
    """채팅방 전체 메시지의 반응 조회"""
    return await find_reactions_usecase.findReactionsByRoom(room_id)
