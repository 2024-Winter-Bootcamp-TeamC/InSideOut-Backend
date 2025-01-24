import pytest
from database import clear_db
from unittest.mock import AsyncMock, patch, MagicMock
from main import app
from fastapi.testclient import TestClient
from unittest.mock import ANY
from sqlalchemy.orm import Session
@pytest.fixture
def client():
    """FastAPI TestClient 생성"""
    return TestClient(app)
@patch("crud.report.get_reports_by_user_id")
def test_report_list_success(mock_get_reports_by_user_id, client):
    mock_get_reports_by_user_id.return_value = [
        {"report_id": 1, "category": "test_category", "title": "test_title"},
    ]
    response = client.get("/api/reports/1")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Data fetch successfuly",
        "data": [{"report_id": 1, "category": "test_category", "title": "test_title"}],
    }
    mock_get_reports_by_user_id.assert_called_once_with(1, ANY)
@pytest.mark.asyncio
@patch("crud.report.redis_client", new_callable=AsyncMock)
@patch("crud.report.post_report_by_user_id", new_callable=AsyncMock)
async def test_create_report_with_explicit_get(mock_post_report_by_user_id, mock_redis_client):
    test_user_id = 1
    test_chatroom_id = 1
    mock_post_report_by_user_id.return_value = 1
    redis_data = {
        f"category_{test_user_id}": "test_category",
        f"content_{test_user_id}": "test_situation_summary",
        f"chat_user_input_{test_chatroom_id}": "test_client_message",
        f"chat_{test_chatroom_id}": "test_emotion_message",
    }
    mock_redis_client.get = AsyncMock(side_effect=lambda key: redis_data.get(key))
    mock_redis_client.set = AsyncMock()
    for key, value in redis_data.items():
        await mock_redis_client.set(key, value)
    category = await mock_redis_client.get(f"category_{test_user_id}")
    situation_summary = await mock_redis_client.get(f"content_{test_user_id}")
    client_message = await mock_redis_client.get(f"chat_user_input_{test_chatroom_id}")
    emotion_message = await mock_redis_client.get(f"chat_{test_chatroom_id}")
    assert category == "test_category"
    assert situation_summary == "test_situation_summary"
    assert client_message == "test_client_message"
    assert emotion_message == "test_emotion_message"
    client = TestClient(app)
    response = client.post(
        f"/api/reports/{test_user_id}?chatroom_id={test_chatroom_id}",
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Data posted successfully",
        "report_id": 1,
    }
    mock_post_report_by_user_id.assert_called_once_with(test_user_id, test_chatroom_id, ANY)
    mock_redis_client.get.assert_any_call(f"category_{test_user_id}")
    mock_redis_client.get.assert_any_call(f"content_{test_user_id}")
    mock_redis_client.get.assert_any_call(f"chat_user_input_{test_chatroom_id}")
    mock_redis_client.get.assert_any_call(f"chat_{test_chatroom_id}")
def test_find_report(client):
    test_report_id = 1
    mock_report_data = {
        "title": "Test Report",
        "situation_summary" : "This is a test situation summary",
        "emotion_summary": {"happy": "50%", "sad": "50%"},
        "wording": {"Happy": "Stay positive!"},
        "emotion_percentage": {"1": 50.0, "2": 50.0},
    }
    with patch("crud.report.get_report_by_report_id") as mock_get_report:
        mock_get_report.return_value = mock_report_data
        response = client.get(f"/api/reports/view/{test_report_id}")
        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "message": "successfully",
            "title": "Test Report",
            "situation_summary": "This is a test situation summary",
            "emotion_summary": {"happy": "50%", "sad": "50%"},
            "wording": {"Happy": "Stay positive!"},
            "emotion_percentage": {"1": 50.0, "2": 50.0},
        }
        mock_get_report.assert_called_once_with(test_report_id, ANY)
def test_report_delete(client):
    test_report_id = 1
    mock_response = {"status": "success", "message": "Report deleted successfully"}
    with patch("crud.report.delete_report_by_report_id") as mock_delete_report:
        mock_delete_report.return_value = mock_response
        response = client.delete(f"/api/reports/{test_report_id}")
        assert response.status_code == 200
        assert response.json() == mock_response
        mock_delete_report.assert_called_once_with(test_report_id, ANY)