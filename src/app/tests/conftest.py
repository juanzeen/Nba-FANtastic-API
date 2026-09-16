import pytest
from ..main import app
from ..dependencies import get_redis
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture(autouse=True)
def mock_redis():
    redis = MagicMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.incr = AsyncMock(return_value=1)
    redis.expire = AsyncMock()
    app.dependency_overrides[get_redis] = lambda: redis
    yield redis
    app.dependency_overrides.pop(get_redis, None)
