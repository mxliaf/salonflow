from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Servico(Base):
    __tablename__ = "servicos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    duracao_minutos: Mapped[int] = mapped_column(Integer, nullable=False)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    agendamentos = relationship("Agendamento", back_populates="servico")
