from fastapi import APIRouter, Depends, HTTPException
from starlette.websockets import WebSocket

from application.port.input.userUsecase import FindUserByUserIdUsecase
from application.service.userService import FindUserService
from common.security import get_access_token
from domain.messageRequest import SendMessageRequest
from application.service.messageService import FindSavedMessageService, SaveAndSendMessageService, \
    SubscribeMessageService
from application.port.input.messageUsecase import SaveAndSendMessageUsecase, \
    FindSavedMessageUsecase, SubscribeMessageUsecase
from domain.orm import User
from domain.response import UserSchema

router = APIRouter(prefix="/hl-chat")

@router.post("", status_code=200)
async def sendMessage(
        request: SendMessageRequest,
        access_token = Depends(get_access_token),
        message_handler: SaveAndSendMessageUsecase = Depends(SaveAndSendMessageService)
):
    await message_handler.saveAndSendMessage(request)

@router.websocket("/{room_id}")
async def websocket_endpoint(
        room_id: int,
        websocket: WebSocket,
        findSavedMessageUsecase: FindSavedMessageUsecase = Depends(FindSavedMessageService),
        subscribeMessageUsecase: SubscribeMessageUsecase = Depends(SubscribeMessageService),
        findUserByUserIdUsecase: FindUserByUserIdUsecase = Depends(FindUserService)
):
    await websocket.accept()
    # 첫 메시지로 인증 대기
    authData = await websocket.receive_json()

    if authData.get('type') != 'auth':
        await websocket.close(code=401)
        return

    # user = await verify_token(auth_data.get('token'))
    user_id = User.decodeJWT(authData.get('token'))
    user: UserSchema | None = await findUserByUserIdUsecase.findUserByUserId(user_id)
    if not user:
        await websocket.close(code=404, reason="User not found")
        return

    print("websocket accepted")
    await findSavedMessageUsecase.findSavedMessage(room_id=room_id, websocket=websocket)
    print("message founded")
    await subscribeMessageUsecase.subscribeMessage(room_id=room_id, websocket=websocket)
# ws = new WebSocket("ws://127.0.0.1:8000/HLChat/room_001");