from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from application.port.input.messageUsecase import SaveAndSendMessageUsecase, \
    SubscribeMessageUsecase, FindSavedMessageUsecase
from application.port.input.roomUsecase import FindAllRoomsByUserIdUsecase, \
    FindAndSendAllRoomsLastMessagesUsecase
from application.port.input.userUsecase import FindUserByUserIdUsecase
from application.service.messageService import SaveAndSendMessageService, \
    SubscribeMessageService, FindSavedMessageService
from application.service.roomService import FindAllRoomsByUserIdService, \
    FindAndSendAllRoomsLastMessagesService
from application.service.userService import FindUserWithSocketService
from common.security import get_access_token
from domain.messageRequest import SendMessageRequest
from domain.response import UserSchema, RoomListSchema
from domain.userDomain import UserDomain

router = APIRouter(prefix="/hl-chat")

@router.post("", status_code=200)
async def sendMessage(
        request: SendMessageRequest,
        access_token = Depends(get_access_token),
        message_handler: SaveAndSendMessageUsecase = Depends(SaveAndSendMessageService)
):
    await message_handler.saveAndSendMessage(request)

@router.websocket("")
async def websocket_endpoint(
        websocket: WebSocket,
        findAllRoomsByUserIdUsecase: FindAllRoomsByUserIdUsecase = Depends(FindAllRoomsByUserIdService),
        findAndSendAllRoomsLastMessagesUsecase: FindAndSendAllRoomsLastMessagesUsecase = Depends(FindAndSendAllRoomsLastMessagesService),
        subscribeMessageUsecase: SubscribeMessageUsecase = Depends(SubscribeMessageService),
        findUserByUserIdUsecase: FindUserByUserIdUsecase = Depends(FindUserWithSocketService)
):
    await websocket.accept()
    # 첫 메시지로 인증 대기
    authData = await websocket.receive_json()

    if authData.get('type') != 'auth':
        await websocket.close(code=401)
        return

    # user = await verify_token(auth_data.get('token'))
    userId = UserDomain.decodeJWT(authData.get('token'))
    user: UserSchema | None = await findUserByUserIdUsecase.findUserByUserId(userId)
    if not user:
        await websocket.close(code=404, reason="User not found")
        return

    print("websocket accepted")
    roomList: RoomListSchema = await findAllRoomsByUserIdUsecase.findAllRoomsByUserId(userId=userId)
    await findAndSendAllRoomsLastMessagesUsecase.findAndSendAllRoomsLastMessages(userId=userId, roomList=roomList, websocket=websocket)
    print("message founded")
    await subscribeMessageUsecase.subscribeMessage(roomList=roomList, websocket=websocket, userId=userId)

# 특정 채팅방의 메시지를 50개씩 가져옴.
@router.get("/{room_id}")
async def findAllRoomsByRoomId(
        room_id: int,
        findSavedMessagesByRoomIdUsecase: FindSavedMessageUsecase = Depends(FindSavedMessageService)
):
    return await findSavedMessagesByRoomIdUsecase.findSavedMessagesByRoomId(room_id)