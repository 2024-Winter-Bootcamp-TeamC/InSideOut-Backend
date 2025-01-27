import unittest
from unittest.mock import patch, MagicMock
from schemas.chatroom import EmotionChooseRequest
from routers.chatroom import create_chatroom_with_emotions

class TestChatroomRouter(unittest.TestCase):
    def test_create_chatroom_with_emotions(self):
        test_user_id = 1
        test_chatroom_id = 100
        test_emotion_ids = [1, 2, 3]

        request_data = EmotionChooseRequest(emotion_ids=test_emotion_ids)

        with patch(
            "routers.chatroom.create_chatroom", return_value=test_chatroom_id
        ) as mock_create_chatroom, patch(
            "routers.chatroom.create_emotion_chooses", return_value=test_emotion_ids
        ) as mock_create_emotion_chooses:
            mock_db = MagicMock()
            result = create_chatroom_with_emotions(
                user_id=test_user_id, request=request_data, db=mock_db
            )

            print("Mock create_chatroom call args:", mock_create_chatroom.call_args)
            print("Mock create_emotion_chooses call args:", mock_create_emotion_chooses.call_args)

            self.assertEqual(result["chatroom_id"], test_chatroom_id)
            self.assertEqual(result["emotion_choose_ids"], test_emotion_ids)

            mock_create_chatroom.assert_called_once_with(mock_db, test_user_id)
            mock_create_emotion_chooses.assert_called_once_with(
                mock_db, test_chatroom_id, test_emotion_ids
            )


if __name__ == "__main__":
    unittest.main()
