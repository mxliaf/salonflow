from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.agendamento import StatusAgendamento
from app.schemas.servico import ServicoRead
from app.schemas.usuario import UsuarioRead


class AgendamentoCreate(BaseModel):
    servico_id: int
    funcionario_id: int | None = None
    data_hora_inicio: datetime

class AgendamentoRead(BaseModel):
    id: int
    cliente_id: int
    servico_id: int
    funcionario_id: int | None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    status: StatusAgendamento
    data_criacao: datetime

    cliente: UsuarioRead | None = None
    funcionario: UsuarioRead | None = None
    servico: ServicoRead | None = None

    model_config = ConfigDict(from_attributes=True)

class SlotDisponivel(BaseModel):
    horario_inicio: datetime
    horario_fim: datetime
    disponivel: bool
