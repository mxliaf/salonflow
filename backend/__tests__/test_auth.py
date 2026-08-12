import pytest
from httpx import AsyncClient
from app.models import Usuario


@pytest.mark.asyncio
async def test_cadastrar_novo_usuario(client: AsyncClient):
    payload = {
        "nome": "Novo Cliente",
        "email": "novo@teste.com",
        "senha": "senha123",
    }

    response = await client.post("/api/auth/cadastrar", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "CLIENTE"


@pytest.mark.asyncio
async def test_cadastrar_email_duplicado_retorna_409(client: AsyncClient, test_cliente: Usuario):
    payload = {
        "nome": "Outro Nome",
        "email": test_cliente.email,
        "senha": "senha123",
    }

    response = await client.post("/api/auth/cadastrar", json=payload)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_com_sucesso(client: AsyncClient, test_cliente: Usuario):
    form_data = {"username": test_cliente.email, "password": "senha123"}

    response = await client.post("/api/auth/login", data=form_data)

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == test_cliente.email


@pytest.mark.asyncio
async def test_login_com_senha_incorreta_retorna_401(client: AsyncClient, test_cliente: Usuario):
    form_data = {"username": test_cliente.email, "password": "senha_errada"}

    response = await client.post("/api/auth/login", data=form_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_retorna_usuario_autenticado(
    client: AsyncClient, test_cliente: Usuario, cliente_headers: dict
):
    response = await client.get("/api/auth/me", headers=cliente_headers)

    assert response.status_code == 200
    assert response.json()["email"] == test_cliente.email


@pytest.mark.asyncio
async def test_get_me_sem_token_retorna_401(client: AsyncClient):
    response = await client.get("/api/auth/me")

    assert response.status_code == 401
