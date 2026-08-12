import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Usuario, Servico
from scripts.seed import seed_usuarios, seed_servicos
from scripts.seed_data import USUARIOS, SERVICOS


@pytest.mark.asyncio
async def test_seed_usuarios_cria_usuarios_esperados(db_session: AsyncSession):
    await seed_usuarios(db_session)
    await db_session.commit()

    result = await db_session.execute(select(Usuario))
    emails = {u.email for u in result.scalars().all()}

    assert emails == {u["email"] for u in USUARIOS}


@pytest.mark.asyncio
async def test_seed_usuarios_e_idempotente(db_session: AsyncSession):
    await seed_usuarios(db_session)
    await db_session.commit()
    await seed_usuarios(db_session)
    await db_session.commit()

    result = await db_session.execute(select(Usuario))
    assert len(result.scalars().all()) == len(USUARIOS)


@pytest.mark.asyncio
async def test_seed_servicos_cria_servicos_esperados(db_session: AsyncSession):
    await seed_servicos(db_session)
    await db_session.commit()

    result = await db_session.execute(select(Servico))
    nomes = {s.nome for s in result.scalars().all()}

    assert nomes == {s["nome"] for s in SERVICOS}


@pytest.mark.asyncio
async def test_seed_servicos_e_idempotente(db_session: AsyncSession):
    await seed_servicos(db_session)
    await db_session.commit()
    await seed_servicos(db_session)
    await db_session.commit()

    result = await db_session.execute(select(Servico))
    assert len(result.scalars().all()) == len(SERVICOS)
