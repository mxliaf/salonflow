
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin
from app.database import get_session
from app.repositories import ServicoRepository
from app.schemas.servico import ServicoCreate, ServicoRead, ServicoUpdate

router = APIRouter(prefix="/api/servicos", tags=["Serviços"])

@router.get("", response_model=list[ServicoRead])
async def listar_servicos(
    apenas_ativos: bool = True,
    db: AsyncSession = Depends(get_session)
):
    repo = ServicoRepository(db)
    servicos = await repo.get_all(apenas_ativos=apenas_ativos)
    return servicos

@router.get("/{servico_id}", response_model=ServicoRead)
async def obter_servico(servico_id: int, db: AsyncSession = Depends(get_session)):
    repo = ServicoRepository(db)
    servico = await repo.get_by_id(servico_id)
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    return servico

@router.post("", response_model=ServicoRead, status_code=status.HTTP_201_CREATED)
async def criar_servico(
    servico_in: ServicoCreate,
    db: AsyncSession = Depends(get_session),
    _admin = Depends(get_current_admin)
):
    repo = ServicoRepository(db)
    servico = await repo.create(servico_in)
    return servico

@router.put("/{servico_id}", response_model=ServicoRead)
async def atualizar_servico(
    servico_id: int,
    servico_in: ServicoUpdate,
    db: AsyncSession = Depends(get_session),
    _admin = Depends(get_current_admin)
):
    repo = ServicoRepository(db)
    servico = await repo.update(servico_id, servico_in)
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    return servico

@router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desativar_servico(
    servico_id: int,
    db: AsyncSession = Depends(get_session),
    _admin = Depends(get_current_admin)
):
    repo = ServicoRepository(db)
    sucesso = await repo.delete(servico_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
