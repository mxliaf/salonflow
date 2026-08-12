import pytest
from httpx import AsyncClient
from app.models import Servico


@pytest.mark.asyncio
async def test_listar_servicos(client: AsyncClient, test_servico: Servico):
    response = await client.get("/api/servicos")

    assert response.status_code == 200
    assert any(s["id"] == test_servico.id for s in response.json())


@pytest.mark.asyncio
async def test_obter_servico_inexistente_retorna_404(client: AsyncClient):
    response = await client.get("/api/servicos/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_criar_servico_requer_admin(client: AsyncClient, cliente_headers: dict):
    payload = {"nome": "Novo Serviço", "duracao_minutos": 30, "preco": 50.0}

    response = await client.post("/api/servicos", json=payload, headers=cliente_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_criar_servico_como_admin(client: AsyncClient, admin_headers: dict):
    payload = {"nome": "Novo Serviço", "duracao_minutos": 30, "preco": 50.0}

    response = await client.post("/api/servicos", json=payload, headers=admin_headers)

    assert response.status_code == 201
    assert response.json()["nome"] == payload["nome"]


@pytest.mark.asyncio
async def test_atualizar_servico_como_admin(client: AsyncClient, admin_headers: dict, test_servico: Servico):
    response = await client.put(
        f"/api/servicos/{test_servico.id}", json={"preco": 150.0}, headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["preco"] == 150.0


@pytest.mark.asyncio
async def test_desativar_servico_como_admin(client: AsyncClient, admin_headers: dict, test_servico: Servico):
    response = await client.delete(f"/api/servicos/{test_servico.id}", headers=admin_headers)

    assert response.status_code == 204
