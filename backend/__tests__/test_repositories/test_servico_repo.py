import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.servico import ServicoRepository
from app.models import Servico
from app.schemas.servico import ServicoCreate, ServicoUpdate


@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession, test_servico: Servico):
    repo = ServicoRepository(db_session)

    servico = await repo.get_by_id(test_servico.id)

    assert servico is not None
    assert servico.nome == test_servico.nome


@pytest.mark.asyncio
async def test_get_all_filtra_apenas_ativos_por_padrao(db_session: AsyncSession, test_servico: Servico):
    repo = ServicoRepository(db_session)
    await repo.delete(test_servico.id)

    ativos = await repo.get_all(apenas_ativos=True)
    todos = await repo.get_all(apenas_ativos=False)

    assert test_servico.id not in [s.id for s in ativos]
    assert test_servico.id in [s.id for s in todos]


@pytest.mark.asyncio
async def test_create_servico(db_session: AsyncSession):
    repo = ServicoRepository(db_session)
    servico_in = ServicoCreate(nome="Escova", duracao_minutos=45, preco=70.0)

    servico = await repo.create(servico_in)

    assert servico.id is not None
    assert servico.ativo is True


@pytest.mark.asyncio
async def test_update_servico(db_session: AsyncSession, test_servico: Servico):
    repo = ServicoRepository(db_session)
    update_in = ServicoUpdate(preco=99.9)

    atualizado = await repo.update(test_servico.id, update_in)

    assert atualizado is not None
    assert atualizado.preco == 99.9


@pytest.mark.asyncio
async def test_update_servico_inexistente_retorna_none(db_session: AsyncSession):
    repo = ServicoRepository(db_session)

    atualizado = await repo.update(99999, ServicoUpdate(preco=10.0))

    assert atualizado is None


@pytest.mark.asyncio
async def test_delete_e_soft_delete(db_session: AsyncSession, test_servico: Servico):
    repo = ServicoRepository(db_session)

    sucesso = await repo.delete(test_servico.id)
    servico = await repo.get_by_id(test_servico.id)

    assert sucesso is True
    assert servico.ativo is False
