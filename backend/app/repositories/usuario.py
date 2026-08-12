from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import get_password_hash
from app.models.usuario import RoleEnum, Usuario
from app.schemas.usuario import UsuarioCreate


class UsuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Usuario | None:
        result = await self.db.execute(select(Usuario).where(Usuario.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_in: UsuarioCreate) -> Usuario:
        hashed_password = get_password_hash(user_in.senha)
        db_user = Usuario(
            nome=user_in.nome,
            email=user_in.email,
            senha_hash=hashed_password,
            role=user_in.role
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_funcionarios(self) -> Sequence[Usuario]:
        result = await self.db.execute(
            select(Usuario).where(Usuario.role.in_([RoleEnum.ADMIN, RoleEnum.FUNCIONARIO]))
        )
        return result.scalars().all()
