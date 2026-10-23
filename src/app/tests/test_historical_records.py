from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock
import pytest
from ..main import app
from ..dependencies import get_db

mock_1 = {
    "_id": 1,
    "value": 43440,
    "label": "points",
    "title": "Most points of all time",
    "record": "ALL_TIME_PTS",
    "leader_id": 2544,
    "leader_full_name": "LeBron James",
    "is_active": True,
    "details": {"season": "", "team": ""},
}

mock_2 = {
    "_id": 2,
    "value": 15806,
    "label": "assists",
    "title": "Most assists of all time",
    "record": "ALL_TIME_AST",
    "leader_id": 304,
    "leader_full_name": "John Stockton",
    "is_active": False,
    "details": {"season": "", "team": ""},
}


@pytest.mark.anyio
async def test_get_historical_records(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(return_value=[mock_1, mock_2])
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/")
        data = response.json().get("data", [])
        message = response.json().get("message", None)
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(data) == 2
    assert message == "Historical records successfully retrieved."
    mock_collection.find.assert_called_once_with({})
    mock_redis.get.assert_called_once_with("historical_records")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "label,expected_mock",
    [
        ("points", mock_1),
        ("assists", mock_2),
    ],
)
async def test_get_historical_records_with_label_filter(
    mock_redis, label, expected_mock
):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(return_value=[expected_mock])
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/api/v1/historical-records/?label={label}")
        body = response.json()
        data = body.get("data", [])
        message = body.get("message", None)
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert message == "Historical records successfully retrieved."
    assert len(data) == 1
    assert data[0]["label"] == label
    assert data[0]["record"] == expected_mock["record"]
    mock_collection.find.assert_called_once_with({"label": label})
    mock_redis.get.assert_called_once_with(f"historical_records:label:{label}")


@pytest.mark.anyio
async def test_fail_get_historical_records_with_valid_label_not_found(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(return_value=[])
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/?label=blocks")
        message = response.json().get("detail", {}).get("message", None)
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Historical records not found."
    mock_collection.find.assert_called_once_with({"label": "blocks"})


@pytest.mark.anyio
async def test_fail_get_historical_records_with_invalid_label(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/?label=invalid_label")
        detail = response.json().get("detail")[0]
    app.dependency_overrides.clear()
    assert response.status_code == 422
    assert detail.get("type") == "literal_error"
    mock_collection.find.assert_not_called()


@pytest.mark.anyio
async def test_fail_get_historical_records(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/")
        message = response.json().get("detail", None).get("message", None)
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Historical records not found."


@pytest.mark.anyio
async def test_fail_get_historical_records_empty_array(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(return_value=[])
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/")
        message = response.json().get("detail", None).get("message", None)
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Historical records not found."


@pytest.mark.anyio
async def test_get_historical_record_by_category(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(return_value=mock_1)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/ALL_TIME_PTS")
        data = response.json().get("data", None)
        message = response.json().get("message", [])
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert message == "Historical record ALL_TIME_PTS successfully retrieved."
    assert data is not None


@pytest.mark.anyio
async def test_fail_get_historical_record_by_category_inexistent_category(mock_redis):
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/AL_TIME_PT")
        message = response.json().get("detail").get("message", [])
    app.dependency_overrides.clear()
    assert response.status_code == 404
    assert message == "Historical record AL_TIME_PT not found."


@pytest.mark.anyio
async def test_fail_get_historical_record_by_category_long_category():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/ALL_TIME_POINTS")
        message = response.json().get("detail")[0].get("msg")
        detail = response.json().get("detail")[0].get("type")
    app.dependency_overrides.clear()
    assert response.status_code == 422
    assert detail == "string_too_long"
    assert message == "String should have at most 13 characters"


@pytest.mark.anyio
async def test_fail_get_historical_record_by_category_short_category():
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.find_one = AsyncMock(return_value=None)
    mock_db.__getitem__.return_value = mock_collection
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/historical-records/AA")
        message = response.json().get("detail")[0].get("msg")
        detail = response.json().get("detail")[0].get("type")
    app.dependency_overrides.clear()
    assert response.status_code == 422
    assert detail == "string_too_short"
    assert message == "String should have at least 8 characters"
