from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.ws_manager import ws_manager

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/agendamentos")
async def websocket_agendamentos(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Mantém a conexão aberta aguardando mensagens de ping/heartbeat do cliente
            _data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
