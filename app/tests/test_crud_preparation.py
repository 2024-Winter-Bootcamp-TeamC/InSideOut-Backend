import unittest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from fastapi import UploadFile
import io
import json
from crud.preparation import file


class TestPreparationCrud(unittest.IsolatedAsyncioTestCase):
    #given
    def setUp(self):
        self.user_id = 1
        self.category = "test_category"
        self.content = "test_content"
        self.files = [
            UploadFile(
                filename="test_image.jpeg",
                file=io.BytesIO(b"dummy image data")
            )
        ]

    @patch("crud.preparation.redis_save", new_callable=AsyncMock)
    @patch("crud.preparation.seven_ai_one_response", new_callable=AsyncMock) 
    @patch("utils.vision.process_user_images", new_callable=AsyncMock)
    async def test_file_preparation(self, mock_vision, mock_ai, mock_redis_save):
        mock_vision.return_value = "dummy image data"
        mock_ai.return_value = {
            "기쁨이": "Mock 기쁨이의 한 줄 조언입니다.",
            "슬픔이": "Mock 슬픔이의 한 줄 조언입니다.",
            "버럭이": "Mock 버럭이의 한 줄 조언입니다.",
            "까칠이": "Mock 까칠이의 한 줄 조언입니다.",
            "소심이": "Mock 소심이의 한 줄 조언입니다.",
            "불안이": "Mock 불안이의 한 줄 조언입니다.",
            "당황이": "Mock 당황이의 한 줄 조언입니다."
        }
        mock_redis_save.return_value = None

        # When
        result = await file(
            db=AsyncMock(spec=Session),
            user_id=self.user_id,
            category=self.category,
            files=self.files,
            content=self.content
        )

        # Then
        self.assertEqual(result["message"], "success")

        mock_vision.assert_called_once_with(self.user_id)

        expected_prompts = json.dumps({
            "category": self.category,
            "content": self.content,
            "image": "dummy image data"
        }, ensure_ascii=False)
        mock_ai.assert_called_once_with(expected_prompts)

        mock_redis_save.assert_called_once_with(
            self.user_id,
            f"user_{self.user_id}",
            {"category": self.category, "content": self.content, "image": "dummy image data"},
            self.category,
            self.content,
            mock_ai.return_value
        )


if __name__ == "__main__":
    unittest.main()
