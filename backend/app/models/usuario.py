import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    CLIENTE = "CLIENTE"
    ADMIN = "ADMIN"
    FUNCIONARIO = "FUNCIONARIO"

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.CLIENTE, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    agendamentos_cliente = relationship(
        "Agendamento",
        foreign_keys="[Agendamento.cliente_id]",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )
    agendamentos_funcionario = relationship(
        "Agendamento",
        foreign_keys="[Agendamento.funcionario_id]",
        back_populates="funcionario"
    )
