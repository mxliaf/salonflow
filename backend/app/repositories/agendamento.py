from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agendamento import Agendamento, StatusAgendamento


class AgendamentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, agendamento_id: int) -> Agendamento | None:
        stmt = (
            select(Agendamento)
            .options(
                selectinload(Agendamento.cliente),
                selectinload(Agendamento.funcionario),
                selectinload(Agendamento.servico)
            )
            .where(Agendamento.id == agendamento_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_cliente(self, cliente_id: int) -> Sequence[Agendamento]:
        stmt = (
            select(Agendamento)
            .options(
                selectinload(Agendamento.servico),
                selectinload(Agendamento.funcionario)
            )
            .where(Agendamento.cliente_id == cliente_id)
            .order_by(Agendamento.data_hora_inicio.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all(self) -> Sequence[Agendamento]:
        stmt = (
            select(Agendamento)
            .options(
                selectinload(Agendamento.cliente),
                selectinload(Agendamento.funcionario),
                selectinload(Agendamento.servico)
            )
            .order_by(Agendamento.data_hora_inicio.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_existentes_no_periodo(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        funcionario_id: int | None = None
    ) -> Sequence[Agendamento]:
        filters = [
            Agendamento.status != StatusAgendamento.CANCELADO,
            Agendamento.data_hora_inicio < data_fim,
            Agendamento.data_hora_fim > data_inicio,
        ]
        if funcionario_id is not None:
            filters.append(Agendamento.funcionario_id == funcionario_id)

        stmt = select(Agendamento).where(and_(*filters))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def check_conflito_horario(
        self,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        funcionario_id: int | None = None
    ) -> bool:
        """
        Retorna True se HOUVER conflito com agendamento existente (sobreposição de horários).
        """
        filters = [
            Agendamento.status != StatusAgendamento.CANCELADO,
            Agendamento.data_hora_inicio < data_hora_fim,
            Agendamento.data_hora_fim > data_hora_inicio
        ]
        if funcionario_id is not None:
            filters.append(
                or_(
                    Agendamento.funcionario_id == funcionario_id,
                    Agendamento.funcionario_id.is_(None)
                )
            )

        stmt = select(Agendamento).where(and_(*filters))
        result = await self.db.execute(stmt)
        existing = result.scalars().first()
        return existing is not None

    async def create(
        self,
        cliente_id: int,
        servico_id: int,
        funcionario_id: int | None,
        data_hora_inicio: datetime,
        data_hora_fim: datetime
    ) -> Agendamento:
        db_agendamento = Agendamento(
            cliente_id=cliente_id,
            servico_id=servico_id,
            funcionario_id=funcionario_id,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            status=StatusAgendamento.CONFIRMADO
        )
        self.db.add(db_agendamento)
        await self.db.commit()
        await self.db.refresh(db_agendamento)
        return await self.get_by_id(db_agendamento.id) # type: ignore

    async def update_status(self, agendamento_id: int, status: StatusAgendamento) -> Agendamento | None:
        db_agendamento = await self.get_by_id(agendamento_id)
        if not db_agendamento:
            return None
        db_agendamento.status = status
        await self.db.commit()
        await self.db.refresh(db_agendamento)
        return db_agendamento
