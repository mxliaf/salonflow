from datetime import UTC, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agendamento import StatusAgendamento
from app.models.usuario import RoleEnum, Usuario
from app.repositories import AgendamentoRepository, ServicoRepository
from app.schemas.agendamento import AgendamentoCreate, AgendamentoRead
from app.services.ws_manager import ws_manager


class AgendamentoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agendamento_repo = AgendamentoRepository(db)
        self.servico_repo = ServicoRepository(db)


    async def criar_agendamento(
        self, cliente_id: int, agendamento_in: AgendamentoCreate
    ) -> AgendamentoRead:
        servico = await self.servico_repo.get_by_id(agendamento_in.servico_id)
        if not servico or not servico.ativo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Serviço especificado não foi encontrado ou está inativo"
            )

        inicio = agendamento_in.data_hora_inicio
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=UTC)

        duracao = timedelta(minutes=servico.duracao_minutos)
        fim = inicio + duracao

        # Validar conflito de horário
        tem_conflito = await self.agendamento_repo.check_conflito_horario(
            data_hora_inicio=inicio,
            data_hora_fim=fim,
            funcionario_id=agendamento_in.funcionario_id
        )

        if tem_conflito:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Horário indisponível! Já existe um agendamento para este período."
            )

        agendamento = await self.agendamento_repo.create(
            cliente_id=cliente_id,
            servico_id=agendamento_in.servico_id,
            funcionario_id=agendamento_in.funcionario_id,
            data_hora_inicio=inicio,
            data_hora_fim=fim
        )

        agendamento_read = AgendamentoRead.model_validate(agendamento)

        # Notificar painel administrativo em tempo real via WebSocket
        await ws_manager.broadcast_json({
            "event": "NOVO_AGENDAMENTO",
            "agendamento": agendamento_read.model_dump(mode="json")
        })

        return agendamento_read

    async def cancelar_agendamento(
        self, agendamento_id: int, usuario_atual: Usuario
    ) -> AgendamentoRead:
        agendamento = await self.agendamento_repo.get_by_id(agendamento_id)
        if not agendamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agendamento não encontrado"
            )

        # Apenas o próprio cliente ou admin/funcionário pode cancelar
        if (
            usuario_atual.role == RoleEnum.CLIENTE
            and agendamento.cliente_id != usuario_atual.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para cancelar este agendamento"
            )

        updated = await self.agendamento_repo.update_status(
            agendamento_id=agendamento_id,
            status=StatusAgendamento.CANCELADO
        )
        
        agendamento_read = AgendamentoRead.model_validate(updated)

        # Notificar painel administrativo sobre o cancelamento em tempo real
        await ws_manager.broadcast_json({
            "event": "AGENDAMENTO_CANCELADO",
            "agendamento": agendamento_read.model_dump(mode="json")
        })

        return agendamento_read
