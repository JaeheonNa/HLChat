import asyncio

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

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
    # 인증 - START
    authData = await websocket.receive_json()
    if authData.get('type') != 'auth':
        await websocket.close(code=401)
        return
    userId = UserDomain.decodeJWT(authData.get('token'))
    user: UserSchema | None = await findUserByUserIdUsecase.findUserByUserId(userId)
    if not user:
        await websocket.close(code=404, reason="User not found")
        return
    # 인증 - END
    # 소캣 통신 - START
    try:
        roomList: RoomListSchema = await findAllRoomsByUserIdUsecase.findAllRoomsByUserId(userId=userId)
        await findAndSendAllRoomsLastMessagesUsecase.findAndSendAllRoomsLastMessages(userId=userId, roomList=roomList, websocket=websocket)
        await subscribeMessageUsecase.subscribeMessage(roomList=roomList, websocket=websocket, userId=userId)
    except WebSocketDisconnect:
        print(f"Client disconnected: {userId}")
    except asyncio.CancelledError:
        # [중요] 서버가 재시작(Reload)되거나 종료될 때 발생
        print("Server reloading... Closing websocket.")
        try:
            await websocket.close(code=1000, reason="Server Reload")
        except:
            pass

        raise # 에러를 다시 던져서 태스크가 완전히 종료되게 함 (선택사항이나 권장)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await websocket.close(code=1011)
        except:
            pass
    # 소캣 통신 - END

# 특정 채팅방의 메시지를 50개씩 가져옴.
@router.get("/init/{room_id}")
async def findAllRoomsByRoomId(
        room_id: int,
        access_token = Depends(get_access_token),
        findSavedMessagesByRoomIdUsecase: FindSavedMessageUsecase = Depends(FindSavedMessageService)
):
    return await findSavedMessagesByRoomIdUsecase.findSavedMessagesByRoomId(room_id, None)

@router.get("/{room_id}/{message_ln_no}")
async def findAllRoomsByRoomId(
        room_id: int,
        message_ln_no: int | None = None,
        access_token = Depends(get_access_token),
        findSavedMessagesByRoomIdUsecase: FindSavedMessageUsecase = Depends(FindSavedMessageService)
):
    return await findSavedMessagesByRoomIdUsecase.findSavedMessagesByRoomId(room_id, message_ln_no)