import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatusAgendamento(str, enum.Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    servico_id: Mapped[int] = mapped_column(Integer, ForeignKey("servicos.id"), nullable=False)
    funcionario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
    data_hora_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    data_hora_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[StatusAgendamento] = mapped_column(
        Enum(StatusAgendamento), default=StatusAgendamento.CONFIRMADO, nullable=False
    )
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    cliente = relationship("Usuario", foreign_keys=[cliente_id], back_populates="agendamentos_cliente")
    funcionario = relationship("Usuario", foreign_keys=[funcionario_id], back_populates="agendamentos_funcionario")
    servico = relationship("Servico", back_populates="agendamentos")
