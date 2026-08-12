from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: str | None = None
    duracao_minutos: int = Field(..., gt=0, description="Duração do serviço em minutos")
    preco: float = Field(..., ge=0, description="Preço do serviço em Reais")

class ServicoCreate(ServicoBase):
    pass

class ServicoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=100)
    descricao: str | None = None
    duracao_minutos: int | None = Field(None, gt=0)
    preco: float | None = Field(None, ge=0)
    ativo: bool | None = None

class ServicoRead(ServicoBase):
    id: int
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
