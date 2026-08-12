from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.utils import create_access_token, verify_password
from app.database import get_session
from app.models.usuario import Usuario
from app.repositories import UsuarioRepository
from app.schemas.usuario import Token, UsuarioCreate, UsuarioLogin, UsuarioRead

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])

@router.post("/cadastrar", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def cadastrar(user_in: UsuarioCreate, db: AsyncSession = Depends(get_session)):
    repo = UsuarioRepository(db)
    existing = await repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com este e-mail"
        )
    user = await repo.create(user_in)
    return user

@router.post("/login", response_model=Token)
async def login(
    login_data: UsuarioLogin | None = None,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    # Aceita tanto JSON body quanto OAuth2 form data
    email = login_data.email if login_data else form_data.username
    password = login_data.senha if login_data else form_data.password

    repo = UsuarioRepository(db)
    user = await repo.get_by_email(email)
    if not user or not verify_password(password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UsuarioRead.model_validate(user)
    )

@router.get("/me", response_model=UsuarioRead)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.get("/funcionarios", response_model=list[UsuarioRead])
async def listar_funcionarios(db: AsyncSession = Depends(get_session)):
    repo = UsuarioRepository(db)
    funcionarios = await repo.get_funcionarios()
    return funcionarios
