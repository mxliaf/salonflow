from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.servico import Servico
from app.schemas.servico import ServicoCreate, ServicoUpdate


class ServicoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, servico_id: int) -> Servico | None:
        result = await self.db.execute(select(Servico).where(Servico.id == servico_id))
        return result.scalar_one_or_none()

    async def get_all(self, apenas_ativos: bool = True) -> Sequence[Servico]:
        query = select(Servico)
        if apenas_ativos:
            query = query.where(Servico.ativo == True)
        result = await self.db.execute(query.order_by(Servico.nome))
        return result.scalars().all()

    async def create(self, servico_in: ServicoCreate) -> Servico:
        db_servico = Servico(
            nome=servico_in.nome,
            descricao=servico_in.descricao,
            duracao_minutos=servico_in.duracao_minutos,
            preco=servico_in.preco
        )
        self.db.add(db_servico)
        await self.db.commit()
        await self.db.refresh(db_servico)
        return db_servico

    async def update(self, servico_id: int, servico_in: ServicoUpdate) -> Servico | None:
        db_servico = await self.get_by_id(servico_id)
        if not db_servico:
            return None
        
        update_data = servico_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_servico, field, value)
            
        await self.db.commit()
        await self.db.refresh(db_servico)
        return db_servico

    async def delete(self, servico_id: int) -> bool:
        db_servico = await self.get_by_id(servico_id)
        if not db_servico:
            return False
        
        # Soft delete desativando o serviço
        db_servico.ativo = False
        await self.db.commit()
        return True
