import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from app.models import Usuario, Servico, StatusAgendamento

@pytest.mark.asyncio
async def test_criar_agendamento_com_sucesso(
    client: AsyncClient,
    test_cliente: Usuario,
    test_servico: Servico,
    cliente_headers: dict
):
    amanha_10h = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )

    payload = {
        "servico_id": test_servico.id,
        "data_hora_inicio": amanha_10h.isoformat()
    }

    response = await client.post("/api/agendamentos", json=payload, headers=cliente_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["cliente_id"] == test_cliente.id
    assert data["servico_id"] == test_servico.id
    assert data["status"] == StatusAgendamento.CONFIRMADO.value


@pytest.mark.asyncio
async def test_tentativa_agendamento_horario_ocupado_retorna_409(
    client: AsyncClient,
    test_cliente: Usuario,
    test_servico: Servico,
    cliente_headers: dict
):
    amanha_14h = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=14, minute=0, second=0, microsecond=0
    )

    payload = {
        "servico_id": test_servico.id,
        "data_hora_inicio": amanha_14h.isoformat()
    }

    # Primeiro agendamento -> OK
    res1 = await client.post("/api/agendamentos", json=payload, headers=cliente_headers)
    assert res1.status_code == 201

    # Segundo agendamento no MESMO horário -> 409 Conflict
    res2 = await client.post("/api/agendamentos", json=payload, headers=cliente_headers)
    assert res2.status_code == 409
    assert "Horário indisponível" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_cancelar_agendamento(
    client: AsyncClient,
    test_cliente: Usuario,
    test_servico: Servico,
    cliente_headers: dict
):
    amanha_16h = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=16, minute=0, second=0, microsecond=0
    )

    payload = {
        "servico_id": test_servico.id,
        "data_hora_inicio": amanha_16h.isoformat()
    }

    # Criar agendamento
    res_create = await client.post("/api/agendamentos", json=payload, headers=cliente_headers)
    assert res_create.status_code == 201
    agendamento_id = res_create.json()["id"]

    # Cancelar agendamento
    res_cancel = await client.patch(
        f"/api/agendamentos/{agendamento_id}/cancelar",
        headers=cliente_headers
    )
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == StatusAgendamento.CANCELADO.value
