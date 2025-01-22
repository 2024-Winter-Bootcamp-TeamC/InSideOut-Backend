import unittest
from unittest.mock import MagicMock
from schemas.user import UserPostRequest
from crud.user import create_user,find_user, login_user, delete_user
from models import *
from routers import *
from fastapi import HTTPException

class TestUserWithMock(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()

    #유저 생성
    def test_create_user(self):
        test_nickname = "nickname"
        test_password = "password"

        test_user_request = UserPostRequest(nickname=test_nickname, password=test_password)

        fake_user = User(id=1, nickname=test_nickname, password=test_password)

        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        self.mock_db.refresh = MagicMock()

        result = create_user(new_user=test_user_request, db=self.mock_db)

        self.mock_db.add.assert_called_once_with(result) 
        self.mock_db.commit.assert_called_once()         
        self.mock_db.refresh.assert_called_once_with(result) 
        self.assertEqual(result.nickname, fake_user.nickname)  
        self.assertEqual(result.password, fake_user.password) 

    #유저 조회
    def test_find_user(self):
        mock_user = User(id=1, nickname="test_user", password="test_password", is_deleted=False)
        self.mock_db.query().filter().first.return_value = mock_user

        result = find_user(user_id=1, db=self.mock_db)

        self.assertEqual(result, "test_user") 
        self.mock_db.query().filter().first.assert_called_once()  

        self.mock_db.query().filter().first.return_value = None

        with self.assertRaises(HTTPException) as context:
            find_user(user_id=999, db=self.mock_db)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")


    #유저 로그인 성공
    def test_login_user_success(self):
        mock_user = User(id=1, nickname="test_user", password="test_password", is_deleted=False)
        self.mock_db.query().filter().first.return_value = mock_user

        result = login_user(nickname="test_user", password="test_password", db=self.mock_db)

        self.assertEqual(result, {"status": "success", "message": "Successfully logged in", "user_id": 1})
        self.mock_db.query().filter().first.assert_called_once()

    #유저 삭제 성공
    def test_delete_user_success(self):
        mock_user = User(id=1, nickname="test_user", is_deleted=False)
        self.mock_db.query().filter().first.return_value = mock_user

        result = delete_user(user_id=1, db=self.mock_db)

        self.assertEqual(result, {"status": "success", "message": "User deleted successfully"})
        self.assertTrue(mock_user.is_deleted)
        self.mock_db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
