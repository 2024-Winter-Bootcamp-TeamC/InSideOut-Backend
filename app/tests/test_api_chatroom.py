import pytest
from database import clear_db

@pytest.fixture(scope="function", autouse=True)
def clear_tests():
    yield
    clear_db()

# 채팅방 생성
def test_create_chatroom(client, user_id):
    request_data = {
        "emotion_ids": [1, 2, 3]  # 감정 ID 리스트 예시
    }

    response = client.post(f"/api/chatrooms/{user_id}", json=request_data)

    assert response.status_code == 200
    response_data = response.json()

    assert "chatroom_id" in response_data
    assert "emotion_choose_ids" in response_data
    assert len(response_data["emotion_choose_ids"]) == len(request_data["emotion_ids"])