import unittest
from unittest.mock import MagicMock, call, ANY
from sqlalchemy.orm import Session
from models import Chatroom, User
from crud.chatroom import create_chatroom, get_chatroom, delete_chatroom
from fastapi import HTTPException

class TestCrudChatroom(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)

    def test_create_chatroom_success(self):
        test_user_id = 1
        mock_user = User(id=test_user_id)
        mock_chatroom = Chatroom(id=100, user_id=test_user_id)

        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        self.mock_db.add.return_value = None
        self.mock_db.refresh.side_effect = lambda chatroom: setattr(chatroom, 'id', 100)

        chatroom_id = create_chatroom(self.mock_db, test_user_id)

        self.assertEqual(chatroom_id, 100)
        self.mock_db.query.return_value.filter.assert_called_once_with(ANY)
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()

    def test_create_chatroom_user_not_found(self):
        test_user_id = 1
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            create_chatroom(self.mock_db, test_user_id)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "사용자를 찾을 수 없습니다.")

    def test_get_chatroom_success(self):
        test_chatroom_id = 100
        mock_chatroom = Chatroom(id=test_chatroom_id, user_id=1)
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_chatroom

        result = get_chatroom(self.mock_db, test_chatroom_id)

        self.assertEqual(result.id, test_chatroom_id)
        self.assertEqual(result.user_id, 1)

        self.mock_db.query.return_value.filter.assert_called_once_with(ANY)

    def test_get_chatroom_not_found(self):
        test_chatroom_id = 100
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            get_chatroom(self.mock_db, test_chatroom_id)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "채팅방을 찾을 수 없습니다.")

    def test_delete_chatroom_success(self):
        test_chatroom_id = 100
        mock_chatroom = Chatroom(id=test_chatroom_id, user_id=1)

        self.mock_db.query.return_value.filter.side_effect = [
            MagicMock(first=MagicMock(return_value=mock_chatroom)),
            MagicMock(first=MagicMock(return_value=None)) 
        ]

        result = delete_chatroom(self.mock_db, test_chatroom_id)

        self.assertEqual(result, test_chatroom_id)

        
        calls = self.mock_db.query.return_value.filter.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], call(ANY))
        self.assertEqual(calls[1], call(ANY))

        self.mock_db.delete.assert_called_once_with(mock_chatroom)
        self.mock_db.commit.assert_called_once()

    def test_delete_chatroom_not_found(self):
        test_chatroom_id = 100
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(HTTPException) as context:
            delete_chatroom(self.mock_db, test_chatroom_id)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "채팅방을 찾을 수 없습니다.")

if __name__ == "__main__":
    unittest.main()
