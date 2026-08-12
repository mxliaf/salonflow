from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.agendamento import AgendamentoRepository
from app.models import Usuario, Servico, StatusAgendamento


@pytest.mark.asyncio
async def test_create_e_get_by_id(db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico):
    repo = AgendamentoRepository(db_session)
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    fim = inicio + timedelta(minutes=test_servico.duracao_minutos)

    criado = await repo.create(
        cliente_id=test_cliente.id,
        servico_id=test_servico.id,
        funcionario_id=None,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
    )
    buscado = await repo.get_by_id(criado.id)

    assert buscado is not None
    assert buscado.cliente_id == test_cliente.id
    assert buscado.status == StatusAgendamento.CONFIRMADO


@pytest.mark.asyncio
async def test_get_by_cliente(db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico):
    repo = AgendamentoRepository(db_session)
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    fim = inicio + timedelta(minutes=test_servico.duracao_minutos)
    await repo.create(
        cliente_id=test_cliente.id,
        servico_id=test_servico.id,
        funcionario_id=None,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
    )

    agendamentos = await repo.get_by_cliente(test_cliente.id)

    assert len(agendamentos) == 1
    assert agendamentos[0].cliente_id == test_cliente.id


@pytest.mark.asyncio
async def test_check_conflito_horario_detecta_sobreposicao(
    db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico
):
    repo = AgendamentoRepository(db_session)
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    fim = inicio + timedelta(minutes=test_servico.duracao_minutos)
    await repo.create(
        cliente_id=test_cliente.id,
        servico_id=test_servico.id,
        funcionario_id=None,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
    )

    tem_conflito = await repo.check_conflito_horario(data_hora_inicio=inicio, data_hora_fim=fim)
    sem_conflito = await repo.check_conflito_horario(
        data_hora_inicio=fim + timedelta(hours=1),
        data_hora_fim=fim + timedelta(hours=2),
    )

    assert tem_conflito is True
    assert sem_conflito is False


@pytest.mark.asyncio
async def test_update_status(db_session: AsyncSession, test_cliente: Usuario, test_servico: Servico):
    repo = AgendamentoRepository(db_session)
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    fim = inicio + timedelta(minutes=test_servico.duracao_minutos)
    criado = await repo.create(
        cliente_id=test_cliente.id,
        servico_id=test_servico.id,
        funcionario_id=None,
        data_hora_inicio=inicio,
        data_hora_fim=fim,
    )

    atualizado = await repo.update_status(criado.id, StatusAgendamento.CANCELADO)

    assert atualizado.status == StatusAgendamento.CANCELADO
