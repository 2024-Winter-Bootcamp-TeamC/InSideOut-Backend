import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from crud.emotions import get_emotions

@pytest.fixture(scope="function", autouse=True)
def mock_redis():
    with patch("crud.emotions.redis_client") as mock_redis_client:
        yield mock_redis_client

@pytest.fixture(scope="function")
def mock_db():
    return MagicMock(spec=Session)

def test_get_emotions_success(mock_redis, mock_db):
    test_user_id = 1
    test_emotions = {
        "anger": 10,
        "joy": 20,
        "sadness": 30,
        "fear": 40,
        "surprise": 50,
        "trust": 60,
        "anticipation": 70,
    }

    mock_redis.get.return_value = test_emotions

    emotions = get_emotions(test_user_id, mock_db)

    assert emotions == test_emotions

def test_get_emotions_not_found(mock_redis, mock_db):
    test_user_id = 1

    mock_redis.get.return_value = None

    emotions = get_emotions(test_user_id, mock_db)

    # 결과 검증
    assert emotions is None