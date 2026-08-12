
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except (ConnectionError, RuntimeError):
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def shutdown(self):
        for connection in list(self.active_connections):
            try:
                await connection.close()
            except (ConnectionError, RuntimeError):
                logger.debug("Connection already closed during shutdown")
        self.active_connections.clear()

ws_manager = ConnectionManager()