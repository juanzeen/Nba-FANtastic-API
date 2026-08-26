from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock
from starlette.testclient import TestClient as TestClient
import pytest
from ..main import app
from ..dependencies import get_client, get_db

client = TestClient(app)


@pytest.mark.anyio
async def test_health_check():
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
        "services": {"api": "healthy", "database": "healthy"},
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


@pytest.mark.anyio
async def test_get_historical_players():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find.return_value.to_list = AsyncMock(
        return_value=[
            {"_id": 1, "full_name": "Michael Jordan"},
            {"_id": 2, "full_name": "Jerry West"},
        ]
    )
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/historical-players/")
        players = response.json().get("players", [])
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert message == "Historical players successfully retrieved."
    assert len(players) > 0


@pytest.mark.anyio
async def test_fail_get_historical_players():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find.return_value.to_list = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/historical-players/")
        players = response.json().get("players", [])
        message = response.json().get("detail", "").get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "No historical players found."
    assert len(players) == 0


@pytest.mark.anyio
async def test_get_historical_player_by_id():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find_one = AsyncMock(
        return_value={"_id": 1, "full_name": "Michael Jordan"}
    )
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/historical-players/1")
        player = response.json().get("player", [])
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert message == "Player successfully retrieved."
    assert player.get("_id") == 1
    assert player.get("full_name") == "Michael Jordan"


@pytest.mark.anyio
async def test_fail_get_historical_player_by_id():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/historical-players/1")
        message = response.json().get("detail", "").get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Player with id 1 not found."


@pytest.mark.anyio
async def test_get_historical_player_by_query_params():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find_one = AsyncMock(
        return_value={"_id": 1, "full_name": "Michael Jordan"}
    )
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/historical-players/?name=Michael&last_name=Jordan")
        player = response.json().get("player", [])
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert message == "Player successfully retrieved."
    assert player.get("_id") == 1
    assert player.get("full_name") == "Michael Jordan"


@pytest.mark.anyio
async def test_fail_get_historical_player_by_query_params():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/historical-players/?name=Michael&last_name=Jordan")
        message = response.json().get("detail", "").get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Player with name Michael Jordan not found."
