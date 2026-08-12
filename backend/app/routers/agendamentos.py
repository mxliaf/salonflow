from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin, get_current_user
from app.database import get_session
from app.models.usuario import Usuario
from app.repositories import AgendamentoRepository
from app.schemas.agendamento import AgendamentoCreate, AgendamentoRead, SlotDisponivel
from app.services.agendamento_service import AgendamentoService
from app.services.disponibilidade_service import DisponibilidadeService

router = APIRouter(prefix="/api/agendamentos", tags=["Agendamentos"])

@router.get("/disponiveis", response_model=list[SlotDisponivel])
async def listar_horarios_disponiveis(
    data: date = Query(..., description="Data da consulta no formato YYYY-MM-DD"),
    servico_id: int = Query(..., description="ID do serviço selecionado"),
    funcionario_id: int | None = Query(None, description="ID opcional do funcionário"),
    db: AsyncSession = Depends(get_session)
):
    service = DisponibilidadeService(db)
    return await service.calcular_horarios_disponiveis(
        data_consulta=data,
        servico_id=servico_id,
        funcionario_id=funcionario_id
    )

@router.post("", response_model=AgendamentoRead, status_code=status.HTTP_201_CREATED)
async def criar_agendamento(
    agendamento_in: AgendamentoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    service = AgendamentoService(db)
    return await service.criar_agendamento(
        cliente_id=current_user.id,
        agendamento_in=agendamento_in
    )

@router.get("/meus", response_model=list[AgendamentoRead])
async def listar_meus_agendamentos(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    repo = AgendamentoRepository(db)
    agendamentos = await repo.get_by_cliente(cliente_id=current_user.id)
    return [AgendamentoRead.model_validate(a) for a in agendamentos]

@router.get("/salao", response_model=list[AgendamentoRead])
async def listar_agendamentos_salao(
    _admin: Usuario = Depends(get_current_admin),
    db: AsyncSession = Depends(get_session)
):
    repo = AgendamentoRepository(db)
    agendamentos = await repo.get_all()
    return [AgendamentoRead.model_validate(a) for a in agendamentos]

@router.patch("/{agendamento_id}/cancelar", response_model=AgendamentoRead)
async def cancelar_agendamento(
    agendamento_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    service = AgendamentoService(db)
    return await service.cancelar_agendamento(
        agendamento_id=agendamento_id,
        usuario_atual=current_user
    )
