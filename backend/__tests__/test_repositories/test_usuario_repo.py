import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.usuario import UsuarioRepository
from app.models import Usuario, RoleEnum
from app.schemas.usuario import UsuarioCreate


@pytest.mark.asyncio
async def test_get_by_id_retorna_usuario_existente(db_session: AsyncSession, test_cliente: Usuario):
    repo = UsuarioRepository(db_session)

    usuario = await repo.get_by_id(test_cliente.id)

    assert usuario is not None
    assert usuario.email == test_cliente.email


@pytest.mark.asyncio
async def test_get_by_id_retorna_none_quando_nao_existe(db_session: AsyncSession):
    repo = UsuarioRepository(db_session)

    usuario = await repo.get_by_id(99999)

    assert usuario is None


@pytest.mark.asyncio
async def test_get_by_email(db_session: AsyncSession, test_cliente: Usuario):
    repo = UsuarioRepository(db_session)

    usuario = await repo.get_by_email(test_cliente.email)

    assert usuario is not None
    assert usuario.id == test_cliente.id


@pytest.mark.asyncio
async def test_create_gera_hash_de_senha(db_session: AsyncSession):
    repo = UsuarioRepository(db_session)
    user_in = UsuarioCreate(nome="Novo", email="novo_repo@teste.com", senha="senha123")

    usuario = await repo.create(user_in)

    assert usuario.id is not None
    assert usuario.senha_hash != "senha123"


@pytest.mark.asyncio
async def test_get_funcionarios_retorna_apenas_admin_e_funcionario(
    db_session: AsyncSession, test_cliente: Usuario, test_admin: Usuario
):
    repo = UsuarioRepository(db_session)

    funcionarios = await repo.get_funcionarios()

    ids = {u.id for u in funcionarios}
    assert test_admin.id in ids
    assert test_cliente.id not in ids


@pytest.mark.asyncio
async def test_get_by_id_com_mock_session(mock_session: AsyncMock):
    """Teste unitário puro do repository, sem tocar em banco de dados real."""
    fake_usuario = Usuario(id=1, nome="Mock", email="mock@teste.com", senha_hash="hash", role=RoleEnum.CLIENTE)
    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = fake_usuario
    mock_session.execute.return_value = execute_result

    repo = UsuarioRepository(mock_session)
    usuario = await repo.get_by_id(1)

    mock_session.execute.assert_awaited_once()
    assert usuario is fake_usuario
