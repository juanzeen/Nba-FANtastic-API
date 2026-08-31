from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock
import pytest
from ..main import app
from ..dependencies import get_db

mock_p1 = {
    "_id": 1630173,
    "career": {
        "totals": {
            "games": 467,
            "points": 3721,
            "assists": 511,
            "rebounds": 2792,
            "blocks": 327,
            "steals": 29,
        },
        "avg": {
            "points": 8,
            "assists": 1.1,
            "rebounds": 6,
            "blocks": 0.7,
            "steals": 0.6,
        },
    },
    "country": "Nigeria",
    "full_name": "Precious Achiuwa",
    "height": 203,
    "id": 1630173,
    "position": "Forward",
    "season": {
        "totals": {
            "games": 0,
            "points": 0,
            "assists": 0,
            "rebounds": 0,
            "blocks": 0,
            "steals": 0,
        },
        "avg": {"points": 0, "assists": 0, "rebounds": 0, "blocks": 0, "steals": 0},
    },
    "team": {"abbreviation": "SAC", "name": "Sacramento Kings"},
    "slug": "precious-achiuwa",
}

mock_p2 = {
    "_id": 30212,
    "career": {
        "totals": {
            "games": 467,
            "points": 3721,
            "assists": 511,
            "rebounds": 2792,
            "blocks": 327,
            "steals": 29,
        },
        "avg": {
            "points": 8,
            "assists": 1.1,
            "rebounds": 6,
            "blocks": 0.7,
            "steals": 0.6,
        },
    },
    "country": "Nigeria",
    "full_name": "Precious Achiuwa",
    "height": 203,
    "id": 1630173,
    "position": "Forward",
    "season": {
        "totals": {
            "games": 0,
            "points": 0,
            "assists": 0,
            "rebounds": 0,
            "blocks": 0,
            "steals": 0,
        },
        "avg": {"points": 0, "assists": 0, "rebounds": 0, "blocks": 0, "steals": 0},
    },
    "team": {"abbreviation": "SAC", "name": "Sacramento Kings"},
    "slug": "precious-achiuwa",
}


@pytest.mark.anyio
async def test_get_players():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_collection.count_documents = AsyncMock(return_value=160)
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(return_value=[mock_p1, mock_p2])
    mock_collection.find.return_value = mock_cursor
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
    mock_cursor = MagicMock()
    mock_collection.count_documents = AsyncMock(return_value=458)
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list = AsyncMock(None)
    mock_collection.find.return_value = mock_cursor
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
    mock_collection.find_one = AsyncMock(return_value=mock_p1)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/1630173")
        data = response.json().get("data", None)
        career_games = data.get("career", {}).get("totals", {}).get("games", 0)
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert data.get("_id") == 1630173
    assert data.get("full_name") == "Precious Achiuwa"
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
        response = await ac.get("/players/1231")
        message = response.json().get("detail", "").get("message")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Player with id 1231 not found."


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


@pytest.mark.anyio
async def test_get_historical_player_by_slug():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find_one = AsyncMock(return_value=mock_p1)
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/search/precious-achiuwa")
        player = response.json().get("data", [])
        message = response.json().get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert message == "Player successfully retrieved."
    assert player.get("_id") == 1630173
    assert player.get("full_name") == "Precious Achiuwa"


@pytest.mark.anyio
async def test_fail_get_historical_player_by_slug():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_cursor
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/players/search/precious-achiuwa")
        message = response.json().get("detail", "").get("message", "")
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Player with slug precious-achiuwa not found."
