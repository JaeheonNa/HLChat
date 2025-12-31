from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket

from schema.request import SendMessageRequest
from service.messageService import MessageHandler
from service.messageServiceInterface import MessageHandlerInterface

router = APIRouter(prefix="/hl-chat")

@router.post("/", status_code=200)
def sendMessage(
        request: SendMessageRequest,
        message_handler: MessageHandlerInterface = Depends(MessageHandler)
):
    message_handler.handleMessage(request)

@router.websocket("/{room_id}")
async def websocket_endpoint(room_id: str,
                             websocket: WebSocket,
                             message_handler: MessageHandlerInterface = Depends(MessageHandler)
):
    await websocket.accept()
    await message_handler.getSavedMessage(room_id=room_id, websocket=websocket)
    await message_handler.subscribe_message(room_id=room_id, websocket=websocket)
# ws = new WebSocket("ws://127.0.0.1:8000/HLChat/room_001");