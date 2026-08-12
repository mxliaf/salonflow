import pytest
from unittest.mock import AsyncMock
from app.services.ws_manager import ConnectionManager


@pytest.mark.asyncio
async def test_connect_adiciona_conexao_ativa():
    manager = ConnectionManager()
    ws = AsyncMock()

    await manager.connect(ws)

    ws.accept.assert_awaited_once()
    assert ws in manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_remove_conexao():
    manager = ConnectionManager()
    ws = AsyncMock()
    await manager.connect(ws)

    manager.disconnect(ws)

    assert ws not in manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_json_envia_para_todas_conexoes():
    manager = ConnectionManager()
    ws1, ws2 = AsyncMock(), AsyncMock()
    await manager.connect(ws1)
    await manager.connect(ws2)

    await manager.broadcast_json({"event": "TESTE"})

    ws1.send_json.assert_awaited_once_with({"event": "TESTE"})
    ws2.send_json.assert_awaited_once_with({"event": "TESTE"})


@pytest.mark.asyncio
async def test_broadcast_json_remove_conexoes_com_falha():
    manager = ConnectionManager()
    ws_ok, ws_falho = AsyncMock(), AsyncMock()
    ws_falho.send_json.side_effect = RuntimeError("conexão fechada")
    await manager.connect(ws_ok)
    await manager.connect(ws_falho)

    await manager.broadcast_json({"event": "TESTE"})

    assert ws_falho not in manager.active_connections
    assert ws_ok in manager.active_connections


@pytest.mark.asyncio
async def test_shutdown_fecha_e_limpa_conexoes():
    manager = ConnectionManager()
    ws1, ws2 = AsyncMock(), AsyncMock()
    await manager.connect(ws1)
    await manager.connect(ws2)

    await manager.shutdown()

    ws1.close.assert_awaited_once()
    ws2.close.assert_awaited_once()
    assert manager.active_connections == []
