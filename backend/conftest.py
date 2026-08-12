import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base, get_session
from app.auth.utils import get_password_hash, create_access_token
from app.main import app
from app.models import Usuario, RoleEnum, Servico

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionTest = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionTest() as session:
        yield session

@pytest.fixture
def mock_session() -> AsyncMock:
    """Sessão assíncrona mockada para testes unitários de repository (sem banco real)."""
    return AsyncMock(spec=AsyncSession)

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_session] = _get_test_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_cliente(db_session: AsyncSession) -> Usuario:
    user = Usuario(
        nome="Cliente Teste",
        email="cliente@teste.com",
        senha_hash=get_password_hash("senha123"),
        role=RoleEnum.CLIENTE
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> Usuario:
    admin = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        senha_hash=get_password_hash("admin123"),
        role=RoleEnum.ADMIN
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin

@pytest_asyncio.fixture
async def test_servico(db_session: AsyncSession) -> Servico:
    servico = Servico(
        nome="Corte de Teste",
        descricao="Serviço para testes unitários",
        duracao_minutos=60,
        preco=80.0,
        ativo=True
    )
    db_session.add(servico)
    await db_session.commit()
    await db_session.refresh(servico)
    return servico

@pytest.fixture
def cliente_headers(test_cliente: Usuario) -> dict:
    token = create_access_token(subject=test_cliente.id, role=test_cliente.role.value)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(test_admin: Usuario) -> dict:
    token = create_access_token(subject=test_admin.id, role=test_admin.role.value)
    return {"Authorization": f"Bearer {token}"}
