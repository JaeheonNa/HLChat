from fastapi import APIRouter, Depends

from application.port.input.webSocketUsecase import FindCurrentWebSocketsUsecase
from application.service.webSocketMetaService import FindCurrentWebSocketsService
from common.security import get_access_token

router = APIRouter(prefix="/websocket-meta")

@router.get("/current-situation")
async def get_current_situation(
        access_token: str = Depends(get_access_token),
        findCurrentWebSockets: FindCurrentWebSocketsUsecase = Depends(FindCurrentWebSocketsService)
):
    return findCurrentWebSockets.findCurrentWebSockets()