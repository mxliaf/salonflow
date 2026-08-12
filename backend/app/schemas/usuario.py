from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.usuario import RoleEnum


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    senha: str
    role: RoleEnum = RoleEnum.CLIENTE

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UsuarioRead"

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None

class UsuarioRead(UsuarioBase):
    id: int
    role: RoleEnum
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
