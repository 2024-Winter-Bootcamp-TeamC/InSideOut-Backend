import pytest
from database import clear_db
import io
from unittest.mock import AsyncMock, patch
from fastapi import UploadFile


@pytest.fixture(scope="function", autouse=True)
def clear_tests():
    yield
    clear_db()

@patch("crud.preparation.redis_client", new_callable=AsyncMock)
def test_file_preparation(mock_redis_client, client):
    test_user_id = 1
    test_category = "test_category"
    test_content = "test_content"
    test_file_content = b"file_content"
    test_file = UploadFile(
        filename="test_image.jpeg",
        file=io.BytesIO(test_file_content)
    )
    
    mock_redis_client.set.return_value = None

    response = client.post(
        f"/api/preparations?user_id={test_user_id}&category={test_category}", 
        data={
            "content": test_content, 
        },
        files=[
            ("files", (test_file.filename, test_file.file, "image/jpeg"))
        ]
    )

    assert response.status_code == 200
    assert response.json() == {"message": "success"}

    mock_redis_client.set.assert_called()
