from datetime import UTC, date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.repositories import AgendamentoRepository, ServicoRepository
from app.schemas.agendamento import SlotDisponivel


class DisponibilidadeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.servico_repo = ServicoRepository(db)
        self.agendamento_repo = AgendamentoRepository(db)


    async def calcular_horarios_disponiveis(
        self,
        data_consulta: date,
        servico_id: int,
        funcionario_id: int | None = None
    ) -> list[SlotDisponivel]:
        servico = await self.servico_repo.get_by_id(servico_id)
        if not servico or not servico.ativo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Serviço não encontrado ou inativo"
            )

        open_h, open_m = map(int, settings.SALON_OPEN_TIME.split(":"))
        close_h, close_m = map(int, settings.SALON_CLOSE_TIME.split(":"))

        salon_open = datetime.combine(data_consulta, time(open_h, open_m)).replace(tzinfo=UTC)
        salon_close = datetime.combine(data_consulta, time(close_h, close_m)).replace(tzinfo=UTC)

        agendamentos_existentes = await self.agendamento_repo.get_existentes_no_periodo(
            data_inicio=salon_open,
            data_fim=salon_close,
            funcionario_id=funcionario_id
        )

        slots: list[SlotDisponivel] = []
        duracao = timedelta(minutes=servico.duracao_minutos)
        cursor = salon_open

        # Intervalo fixo de 30 minutos entre slots
        passo_slot = timedelta(minutes=30)

        while cursor + duracao <= salon_close:
            slot_inicio = cursor
            slot_fim = cursor + duracao

            # Verificar sobreposição com agendamentos existentes
            tem_conflito = False
            for ag in agendamentos_existentes:
                # Normaliza timezone para comparação correta
                ag_inicio = ag.data_hora_inicio.astimezone(UTC) if ag.data_hora_inicio.tzinfo else ag.data_hora_inicio.replace(tzinfo=UTC)
                ag_fim = ag.data_hora_fim.astimezone(UTC) if ag.data_hora_fim.tzinfo else ag.data_hora_fim.replace(tzinfo=UTC)

                if slot_inicio < ag_fim and slot_fim > ag_inicio:
                    tem_conflito = True
                    break

            slots.append(SlotDisponivel(
                horario_inicio=slot_inicio,
                horario_fim=slot_fim,
                disponivel=not tem_conflito
            ))

            cursor += passo_slot

        return slots
