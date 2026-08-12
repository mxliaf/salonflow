from datetime import datetime, timedelta, timezone
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.agendamento_service import AgendamentoService
from app.schemas.agendamento import AgendamentoCreate
from app.models import Usuario, Servico, RoleEnum, StatusAgendamento


@pytest.mark.asyncio
async def test_criar_agendamento_com_servico_inativo_levanta_404(
    db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico
):
    test_servico.ativo = False
    await db_session.commit()

    service = AgendamentoService(db_session)
    agendamento_in = AgendamentoCreate(
        servico_id=test_servico.id,
        data_hora_inicio=datetime.now(timezone.utc) + timedelta(days=1),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.criar_agendamento(cliente_id=test_cliente.id, agendamento_in=agendamento_in)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_cancelar_agendamento_de_outro_cliente_levanta_403(
    db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico
):
    service = AgendamentoService(db_session)
    agendamento_in = AgendamentoCreate(
        servico_id=test_servico.id,
        data_hora_inicio=datetime.now(timezone.utc) + timedelta(days=1),
    )
    agendamento = await service.criar_agendamento(cliente_id=test_cliente.id, agendamento_in=agendamento_in)

    outro_cliente = Usuario(
        id=test_cliente.id + 1000,
        nome="Outro",
        email="outro_cliente@teste.com",
        senha_hash="hash",
        role=RoleEnum.CLIENTE,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.cancelar_agendamento(agendamento_id=agendamento.id, usuario_atual=outro_cliente)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_cancelar_agendamento_inexistente_levanta_404(db_session: AsyncSession, test_cliente: Usuario):
    service = AgendamentoService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.cancelar_agendamento(agendamento_id=99999, usuario_atual=test_cliente)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_cancelar_agendamento_pelo_proprio_cliente(
    db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico
):
    service = AgendamentoService(db_session)
    agendamento_in = AgendamentoCreate(
        servico_id=test_servico.id,
        data_hora_inicio=datetime.now(timezone.utc) + timedelta(days=1),
    )
    agendamento = await service.criar_agendamento(cliente_id=test_cliente.id, agendamento_in=agendamento_in)

    cancelado = await service.cancelar_agendamento(agendamento_id=agendamento.id, usuario_atual=test_cliente)

    assert cancelado.status == StatusAgendamento.CANCELADO
