import pytest
from httpx import AsyncClient
from app.models import Usuario


@pytest.mark.asyncio
async def test_listar_funcionarios(client: AsyncClient, test_admin: Usuario, test_cliente: Usuario):
    response = await client.get("/api/auth/funcionarios")

    assert response.status_code == 200
    emails = {f["email"] for f in response.json()}
    assert test_admin.email in emails
    assert test_cliente.email not in emails
