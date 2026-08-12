"""Popula o banco de dados com dados iniciais (idempotente).

Uso:
    DATABASE_URL=postgresql+asyncpg://... python -m scripts.seed
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models import Usuario, RoleEnum, Servico
from app.auth.utils import get_password_hash
from scripts.seed_data import USUARIOS, SERVICOS


async def seed_usuarios(session) -> None:
    for usuario in USUARIOS:
        result = await session.execute(select(Usuario).where(Usuario.email == usuario["email"]))
        if result.scalar_one_or_none():
            continue
        session.add(
            Usuario(
                nome=usuario["nome"],
                email=usuario["email"],
                senha_hash=get_password_hash(usuario["senha"]),
                role=RoleEnum(usuario["role"]),
            )
        )


async def seed_servicos(session) -> None:
    for servico in SERVICOS:
        result = await session.execute(select(Servico).where(Servico.nome == servico["nome"]))
        if result.scalar_one_or_none():
            continue
        session.add(
            Servico(
                nome=servico["nome"],
                descricao=servico["descricao"],
                duracao_minutos=servico["duracao_minutos"],
                preco=servico["preco"],
                ativo=True,
            )
        )


async def seed() -> None:
    async with async_session() as session:
        await seed_usuarios(session)
        await seed_servicos(session)
        await session.commit()
    print("Seed concluído com sucesso.")


if __name__ == "__main__":
    asyncio.run(seed())
