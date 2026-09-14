from unittest.mock import MagicMock, AsyncMock
from ..main import app
from ..dependencies import get_client
from httpx2 import AsyncClient, ASGITransport
import pytest


@pytest.mark.anyio
async def test_health_check(mock_redis):
    mock_client = MagicMock()
    mock_client.admin.command = AsyncMock(return_value={"ok": 1})
    app.dependency_overrides[get_client] = lambda: mock_client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "services": {"api": "healthy", "database": "healthy", "cache": "healthy"},
    }


@pytest.mark.anyio
async def test_unhealth_check():
    mock_client = MagicMock()
    mock_client.admin.command = AsyncMock(
        side_effect=Exception("Database connection error")
    )
    app.dependency_overrides[get_client] = lambda: mock_client
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
        status = response.json().get("detail", "unknown").get("status", "unknown")
    app.dependency_overrides.clear()
    assert response.status_code == 503
    assert status == "unhealthy"
