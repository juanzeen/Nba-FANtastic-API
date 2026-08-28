from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock
import pytest
from ..main import app
from ..dependencies import get_db


@pytest.mark.anyio
async def test_get_players():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(
        return_value=[
            {
                "_id": 1,
                "full_name": "Michael Jordan",
                "country": "USA",
                "weight": 123,
                "height": 192,
            },
            {
                "_id": 2,
                "full_name": "Michael Jordan",
                "country": "USA",
                "weight": 123,
                "height": 192,
            },
        ]
    )
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/")
        data = response.json().get("data", [])
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(data) > 1
    assert message == "Actual NBA players successfully retrieved."


@pytest.mark.anyio
async def test_fail_get_players():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value = AsyncMock(return_value=[])
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/")
        data = response.json().get("data", [])
        message = response.json().get("detail", "").get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert data == []
    assert message == "Actual NBA players not found."


@pytest.mark.anyio
async def test_get_player():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(
        return_value={
            "_id": 1,
            "full_name": "LeBron James",
            "country": "USA",
            "weight": 123,
            "height": 192,
            "career": {"totals": {"games": 1622}},
        }
    )
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/1")
        data = response.json().get("data", None)
        career_games = data.get("career", {}).get("totals", {}).get("games", 0)
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert data.get("_id") == 1
    assert data.get("full_name") == "LeBron James"
    assert career_games > 0
    assert message == "Player successfully retrieved."


@pytest.mark.anyio
async def test_fail_get_player():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/1")
        message = response.json().get("detail", "").get("message")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Player with id: 1 not found."


@pytest.mark.anyio
async def test_fail_get_player_invalid_id_format():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/alsk{tsaxa}123")
        error_type = response.json().get("detail")[0].get("type")
        message = response.json().get("detail")[0].get("msg")
    app.dependency_overrides.clear()
    # 422 is the default error code from FastAPI invalid path param
    assert response.status_code == 422
    assert (
        message
        == "Input should be a valid integer, unable to parse string as an integer"
    )
    assert error_type == "int_parsing"
