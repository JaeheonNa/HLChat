import asyncio

from fastapi import APIRouter, Depends
from redis import Redis
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
from common.redis_pubsub import getRedis
from common.security import get_access_token
from adapter.output.webSocket import WebSocketConnectionManager, get_websocket_connection_manager
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

@router.websocket("/{user_id}")
async def websocket_endpoint(
        user_id: str,
        websocket: WebSocket,
        findAllRoomsByUserIdUsecase: FindAllRoomsByUserIdUsecase = Depends(FindAllRoomsByUserIdService),
        findAndSendAllRoomsLastMessagesUsecase: FindAndSendAllRoomsLastMessagesUsecase = Depends(FindAndSendAllRoomsLastMessagesService),
        subscribeMessageUsecase: SubscribeMessageUsecase = Depends(SubscribeMessageService),
        findUserByUserIdUsecase: FindUserByUserIdUsecase = Depends(FindUserWithSocketService),
        connectionManager: WebSocketConnectionManager = Depends(get_websocket_connection_manager),
        redisSubscriber: Redis = Depends(getRedis)
):

    connectionManager.store_connection(user_id, websocket, redisSubscriber)

    await websocket.accept()
    # 인증 - START
    authData = await websocket.receive_json()
    if authData.get('type') != 'auth':
        await websocket.close(code=401)
        return
    userId = UserDomain.decodeJWT(authData.get('token'))

    if user_id != userId:
        await connectionManager.disconnect(userId, code=401, reason="Unauthorized Access")
        return

    user: UserSchema | None = await findUserByUserIdUsecase.findUserByUserId(userId)
    if not user:
        await connectionManager.disconnect(userId, code=404, reason="User not found")
        return
    # 인증 - END


    # 소캣 통신 - START
    try:
        roomList: RoomListSchema = await findAllRoomsByUserIdUsecase.findAllRoomsByUserId(userId=userId)
        # 사용자가 포함된 모든 방의 가장 최근 메시지 하나씩 전송(MongoDB 조회 -> WebSocket 전송)
        await findAndSendAllRoomsLastMessagesUsecase.findAndSendAllRoomsLastMessages(userId=userId, roomList=roomList)
        # pubsub 등록 후 메시지 수신(Redis Subscribe -> WebSocket 전송)
        await subscribeMessageUsecase.subscribeMessage(roomList=roomList, userId=userId)
    except WebSocketDisconnect:
        print(f"Client disconnected: {userId}")
    except asyncio.CancelledError:
        # [중요] 서버가 재시작(Reload)되거나 종료될 때 발생
        print("Server reloading... Closing websocket.")
        try:
            await connectionManager.disconnect(userId, code=1000, reason="Server Reload")
        except:
            pass

        raise # 에러를 다시 던져서 태스크가 완전히 종료되게 함 (선택사항이나 권장)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await connectionManager.disconnect(userId, code=1011)
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