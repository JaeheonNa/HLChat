from fastapi import Depends

from adapter.output.webSocket import get_websocket_connection_manager, WebSocketConnectionManager
from application.port.input.webSocketUsecase import FindCurrentWebSocketsUsecase


class FindCurrentWebSocketsService(FindCurrentWebSocketsUsecase):
    def __init__(self,
                 singletonWebSocketManager: WebSocketConnectionManager = Depends(get_websocket_connection_manager)
    ):
        self.singletonWebSocketManager = singletonWebSocketManager

    def findCurrentWebSockets(self):
        return list(self.singletonWebSocketManager.active_connections.keys())
