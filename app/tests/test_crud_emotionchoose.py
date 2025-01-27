import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from crud.emotionchoose import create_emotion_chooses
from models import EmotionChoose


class TestCreateEmotionChooses(unittest.TestCase):
    def setUp(self):
        self.chatroom_id = 1
        self.emotion_ids = [101, 102, 103]

    def test_create_emotion_chooses_success(self):
        # Mock DB 세션 생성
        mock_db = MagicMock(spec=Session)

        # create_emotion_chooses 함수 호출
        result = create_emotion_chooses(
            db=mock_db,
            chatroom_id=self.chatroom_id,
            emotion_ids=self.emotion_ids
        )

        # 반환값 검증 (길이 확인)
        self.assertEqual(len(result), len(self.emotion_ids))

        # DB 동작 호출 여부 확인
        self.assertEqual(mock_db.add.call_count, len(self.emotion_ids))
        self.assertEqual(mock_db.commit.call_count, len(self.emotion_ids))
        self.assertEqual(mock_db.refresh.call_count, len(self.emotion_ids))


if __name__ == "__main__":
    unittest.main()
