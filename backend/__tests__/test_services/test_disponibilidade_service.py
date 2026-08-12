from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.disponibilidade_service import DisponibilidadeService
from app.models import Servico


@pytest.mark.asyncio
async def test_calcular_horarios_para_servico_inexistente_levanta_404(db_session: AsyncSession):
    service = DisponibilidadeService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.calcular_horarios_disponiveis(
            data_consulta=date.today() + timedelta(days=1),
            servico_id=99999,
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_calcular_horarios_disponiveis_retorna_slots(db_session: AsyncSession, test_servico: Servico):
    service = DisponibilidadeService(db_session)

    slots = await service.calcular_horarios_disponiveis(
        data_consulta=date.today() + timedelta(days=1),
        servico_id=test_servico.id,
    )

    assert len(slots) > 0
    assert all(slot.disponivel for slot in slots)


@pytest.mark.asyncio
async def test_slots_respeitam_duracao_do_servico(db_session: AsyncSession, test_servico: Servico):
    service = DisponibilidadeService(db_session)

    slots = await service.calcular_horarios_disponiveis(
        data_consulta=date.today() + timedelta(days=1),
        servico_id=test_servico.id,
    )

    for slot in slots:
        duracao = slot.horario_fim - slot.horario_inicio
        assert duracao.total_seconds() / 60 == test_servico.duracao_minutos
