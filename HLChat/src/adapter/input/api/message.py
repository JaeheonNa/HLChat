from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from common.security import get_access_token
from domain.messageRequest import SendMessageRequest
from application.service.messageService import FindSavedMessageService, SaveAndSendMessageService, \
    SubscribeMessageService
from application.port.input.messageUsecase import SaveAndSendMessageUsecase, \
    FindSavedMessageUsecase, SubscribeMessageUsecase

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
        access_token = Depends(get_access_token),
        findSavedMessageUsecase: FindSavedMessageUsecase = Depends(FindSavedMessageService),
        subscribeMessageUsecase: SubscribeMessageUsecase = Depends(SubscribeMessageService)
):
    await websocket.accept()
    print("websocket accepted")
    await findSavedMessageUsecase.findSavedMessage(room_id=room_id, websocket=websocket)
    print("message founded")
    await subscribeMessageUsecase.subscribeMessage(room_id=room_id, websocket=websocket)
# ws = new WebSocket("ws://127.0.0.1:8000/HLChat/room_001");