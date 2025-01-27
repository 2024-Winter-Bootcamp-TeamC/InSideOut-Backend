import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def mock_redis():
    with patch("crud.emotions.redis_client") as mock_redis_client:
        yield mock_redis_client

# Router 테스트: 7가지 감정 조회 성공
def test_seven_emotion_success(mock_redis):
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

    # Redis에서 key 조회 시 반환값 설정
    mock_redis.get.return_value = test_emotions

    response = client.get(f"/api/emotions/{test_user_id}")

    # 응답 검증
    assert response.status_code == 200
    assert response.json() == test_emotions

# Router 테스트: Redis에서 값이 없는 경우
def test_seven_emotion_not_found(mock_redis):
    test_user_id = 1

    # Redis에서 key 조회 시 None 반환
    mock_redis.get.return_value = None

    response = client.get(f"/api/emotions/{test_user_id}")

    # 응답 검증
    assert response.status_code == 200
    assert response.json() is None
